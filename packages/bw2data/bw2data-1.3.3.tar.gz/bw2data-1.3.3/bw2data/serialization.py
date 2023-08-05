# -*- coding: utf-8 -*-
from . import config
from .utils import safe_save
from time import time
import bz2
import os
import random
try:
    import anyjson
except ImportError:
    anyjson = None
    import json
try:
    import cPickle as pickle
except ImportError:
    import pickle


class JsonWrapper(object):
    @classmethod
    def dump(self, data, filepath):
        with safe_save(filepath) as filepath:
            with open(filepath, "wb") as f:
                if anyjson:
                    f.write(anyjson.serialize(data))
                else:
                    json.dump(data, f, indent=2)

    @classmethod
    def dump_bz2(self, data, filepath):
        with safe_save(filepath) as filepath:
            with bz2.BZ2File(filepath, "wb") as f:
                f.write(JsonWrapper.dumps(data))

    @classmethod
    def load(self, file):
        if anyjson:
            return anyjson.deserialize(open(file).read())
        else:
            return json.load(open(file))

    @classmethod
    def load_bz2(self, filepath):
        return JsonWrapper.loads(bz2.BZ2File(filepath).read())

    @classmethod
    def dumps(self, data):
        if anyjson:
            return anyjson.serialize(data)
        else:
            return json.dumps(data)

    @classmethod
    def loads(self, data):
        if anyjson:
            return anyjson.deserialize(data)
        else:
            return json.loads(data)


class JsonSanitizer(object):
    @classmethod
    def sanitize(cls, data):
        if isinstance(data, tuple):
            return {
                '__tuple__': True,
                'data': [cls.sanitize(x) for x in data]
            }
        elif isinstance(data, dict):
            return {
                '__dict__': True,
                'keys': [cls.sanitize(x) for x in data.keys()],
                'values': [cls.sanitize(x) for x in data.values()]
            }
        elif isinstance(data, list):
            return [cls.sanitize(x) for x in data]
        else:
            return data

    @classmethod
    def load(cls, data):
        if isinstance(data, dict):
            if "__tuple__" in data:
                return tuple([cls.load(x) for x in data['data']])
            elif "__dict__" in data:
                return dict(zip(
                    [cls.load(x) for x in data['keys']],
                    [cls.load(x) for x in data['values']]
                ))
            else:
                raise ValueError
        elif isinstance(data, list):
            return [cls.load(x) for x in data]
        else:
            return data


class SerializedDict(object):
    """Base class for dictionary that can be `serialized <http://en.wikipedia.org/wiki/Serialization>`_ to or unserialized from disk. Uses JSON as its storage format. Has most of the methods of a dictionary.

    Upon instantiation, the serialized dictionary is read from disk."""
    def __init__(self, dirpath=None):
        if not getattr(self, "filename"):
            raise NotImplemented("SerializedDict must be subclassed, and the filename must be set.")
        self.filepath = os.path.join(
            dirpath or config.dir,
            self.filename
        )
        self.load()

    def load(self):
        """Load the serialized data. Creates the file if not yet present."""
        try:
            self.data = self.deserialize()
        except IOError:
            # Create if not present
            self.data = {}
            self.flush()

    def flush(self):
        """Serialize the current data to disk."""
        self.serialize()

    @property
    def list(self):
        """List the keys of the dictionary. This is a property, and does not need to be called."""
        return sorted(self.data.keys())

    def __getitem__(self, key):
        if isinstance(key, list):
            key = tuple(key)
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value
        self.flush()

    def __contains__(self, key):
        return key in self.data

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return u"Brightway2 serialized dictionary with {} entries".format(len(self))

    def __delitem__(self, name):
        del self.data[name]
        self.flush()

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return iter(self.data)

    def iteritems(self):
        return self.data.iteritems()

    def keys(self):
        return self.data.keys()

    def values(self):
        return self.data.values()

    def serialize(self, filepath=None):
        """Method to do the actual serialization. Can be replaced with other serialization formats.

        Args:
            * *filepath* (str, optional): Provide an alternate filepath (e.g. for backup).

        """
        with safe_save(filepath or self.filepath) as filepath:
            JsonWrapper.dump(
                self.pack(self.data),
                filepath
            )

    def deserialize(self):
        """Load the serialized data. Can be replaced with other serialization formats."""
        return self.unpack(JsonWrapper.load(self.filepath))

    def pack(self, data):
        """Transform the data, if necessary. Needed because JSON must have strings as dictionary keys."""
        return data

    def unpack(self, data):
        """Return serialized data to true form."""
        return data

    def random(self):
        """Return a random key."""
        if not self.data:
            return None
        else:
            return random.choice(self.data.keys())

    def backup(self):
        """Write a backup version of the data to the ``backups`` directory."""
        filepath = os.path.join(config.dir, "backups",
            self.filename + ".%s.backup" % int(time()))
        self.serialize(filepath)


class PickledDict(SerializedDict):
    """Subclass of ``SerializedDict`` that uses the pickle format instead of JSON."""
    def serialize(self):
        with safe_save(self.filepath) as filepath:
            with open(filepath, "wb") as f:
                pickle.dump(self.pack(self.data), f,
                    protocol=pickle.HIGHEST_PROTOCOL)

    def deserialize(self):
        return self.unpack(pickle.load(open(self.filepath, "rb")))


class CompoundJSONDict(SerializedDict):
    """Subclass of ``SerializedDict`` that allows tuples as dictionary keys (not allowed in JSON)."""
    def pack(self, data):
        """Transform the dictionary to a list because JSON can't handle lists as keys"""
        return [(k, v) for k, v in data.iteritems()]

    def unpack(self, data):
        """Transform data back to a dictionary"""
        return dict([(tuple(x[0]), x[1]) for x in data])
