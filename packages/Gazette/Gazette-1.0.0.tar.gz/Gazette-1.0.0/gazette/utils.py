from __future__ import absolute_import, division, print_function, unicode_literals

import argparse

import jsonpickle
import datastore.core
from datastore.filesystem import FileSystemDatastore
from datastore.core.serialize import SerializerShimDatastore

from gazette.models import Content
from gazette.content_types import all_content_types


def parse_config_args(argv=None):
    """
    Simple arg parser to make common configurations easy.
    If you need a different configuration, you should set it up with a few lines of python to do exactly what you need.

    :param list argv:
    :return: a Datastore
    """
    parser = argparse.ArgumentParser(argv)
    datastores = {
        'fs': FileSystemDatastore,
    }
    serializers = {
        'json': jsonpickle,
    }
    parser.add_argument('--datastore', required=True, choices=datastores.keys())
    parser.add_argument('--path')
    parser.add_argument('--serializer', choices=serializers.keys())
    opts = parser.parse_args(argv)

    ds = datastores[opts.datastore](opts.path)
    if opts.serializer == 'json':
        ds.object_extension = '.json'
    if opts.serializer:
        ds = SerializerShimDatastore(ds, serializer=serializers[opts.serializer])
    return ds


def datastore_json_files(dir):
    """
    Convenience method for a Datastore using local json files

    :param str dir:
    :return: Datastore
    """
    fs_datastore = FileSystemDatastore(dir)
    fs_datastore.object_extension = '.json'
    return SerializerShimDatastore(fs_datastore, serializer=jsonpickle)


class AutoKeyClassDatastore(datastore.core.basic.ShimDatastore):
    '''
    A wrapper around another datastore that automatically converts string "key"
    parameters into instances of the ``Key`` class
    '''

    def delete(self, key):
        if not isinstance(key, datastore.Key):
            key = datastore.Key(key)
        return self.child_datastore.delete(key)

    def get(self, key):
        if not isinstance(key, datastore.Key):
            key = datastore.Key(key)
        return self.child_datastore.get(key)

    def put(self, key, value):
        if not isinstance(key, datastore.Key):
            key = datastore.Key(key)
        return self.child_datastore.put(key, value)

    def query(self, query):
        return self.child_datastore.query(query)


class JsonPickleClean(object):
    @staticmethod
    def dumps(*a, **kw):
        kw.update(unpicklable=False)  # omits "tags" like "py/object": "ClassName"
        return jsonpickle.dumps(*a, **kw)

    @staticmethod
    def loads(*a, **kw):
        return jsonpickle.loads(*a, **kw)


class ContentDictSerializer(object):
    '''
    Serializer/deserializer from Content to dict.

    Perfect for storing into mongo or other datastore that handles dicts.
    '''

    @staticmethod
    def dumps(obj):
        if isinstance(obj, Content):
            return obj.__dict__
        else:
            return obj

    @staticmethod
    def loads(data):
        content_type_name = data.pop('content_type', None)
        if content_type_name:
            content_type = all_content_types()[content_type_name]
            data.pop('key', None)
            return content_type(**data)
        else:
            return data


class MongoNonWrapDatastore(datastore.core.basic.ShimDatastore):
    '''
    Avoids the mongo datastore from wrapping our doc into a nested document,
    by adding the key into the doc itself
    '''

    def get(self, key):
        return self.child_datastore.get(key)

    def put(self, key, value):
        if 'key' not in value:
            value['key'] = str(key)
        return self.child_datastore.put(key, value)

    def delete(self, key):
        return self.child_datastore.delete(key)

    def query(self, query):
        return self.child_datastore.query(query)
