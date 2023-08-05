#!/usr/bin/env python
#
# Copyright (c) 2011-2013, Shopkick Inc.
# All rights reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# ---
# Author: John Egan <jwegan@gmail.com>

import abc
import copy
import os.path

import flawless.lib.config
from flawless.lib.data_structures.persistent_dictionary import PersistentDictionary


class StorageInterface(object):
    """By default Flawless stores everything on disk which means there can only be one centralized instance of
    Flawless. You can implement your own instance of StorageInterface that connects to a backend database and pass
    it into flawless.server.server.serve. Then it is possible to have the flawless server be horizontally scalable
    since the database serves as the centralized source of truth.

    It is worth noting is that the keys used in this interface are either python primitives (string, list, etc) or
    thrift objects. The values can also be python primitives (list, dictionary, etc) or thrift objects
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, partition):
        """partition is a string used to partition keys by week. For instance, with disk storage, we create a new
        file for every unique partition. For a database you may want to consider prepending all keys with
        partition. For accessing config data, the partition is None"""
        self.partition = partition

    def open(self):
        """Called to create connection to storage"""
        pass

    def sync(self):
        """Called periodically to flush data"""
        pass

    def close(self):
        """Called to close connection to storage"""
        pass

    def migrate_thrift_obj(self, obj):
        """Helper function that can be called when serializing/deserializing thrift objects whose definitions
        have changed, we need to make sure we initialize the new attributes to their default value"""
        if not hasattr(obj, "thrift_spec"):
            return

        obj_key_set = set(obj.__dict__.keys())
        thrift_field_map = {t[2]: t[4] for t in obj.thrift_spec if t}
        obj.__dict__.update({f: copy.copy(thrift_field_map[f]) for f in set(thrift_field_map.keys()) - obj_key_set})
        for value in obj.__dict__.itervalues():
            self.migrate_thrift_obj(value)

    @abc.abstractmethod
    def iteritems(self):
        """Should return iterator of tuples (key, value) for all entries for the given self.partition"""
        pass

    @abc.abstractmethod
    def __setitem__(self, key, item):
        pass

    @abc.abstractmethod
    def __getitem__(self, key):
        """Should return None if key does not exist"""
        pass

    @abc.abstractmethod
    def __contains__(self, key):
        pass


class DiskStorage(StorageInterface):

    def __init__(self, partition):
        super(DiskStorage, self).__init__(partition)
        config = flawless.lib.config.get()
        if self.partition:
            filepath = os.path.join(config.data_dir_path, "flawless-errors-", partition)
        else:
            filepath = os.path.join(config.data_dir_path, "flawless-whitelists-config")
        self.disk_dict = PersistentDictionary(filepath)

    def _proxyfunc_(attr, self, *args, **kwargs):
        try:
            return getattr(self.disk_dict, attr)(*args, **kwargs)
        except KeyError:
            return None

    def open(self):
        self.disk_dict.open()

        # Build new copy of dict since migrate_thrift_obj may change the hash code of the keys of the dict
        migrated_dict = dict()
        for key, value in self.disk_dict.dict.items():
            self.migrate_thrift_obj(key)
            self.migrate_thrift_obj(value)
            migrated_dict[key] = value

        self.disk_dict.dict = migrated_dict

    def sync(self):
        self.disk_dict.sync()

    def close(self):
        self.disk_dict.close()

    def iteritems(self):
        return self.disk_dict.dict.iteritems()

    def __setitem__(self, key, item):
        self.disk_dict[key] = item

    def __getitem__(self, key):
        try:
            return self.disk_dict[key]
        except KeyError:
            return None

    def __contains__(self, key):
        return key in self.disk_dict
