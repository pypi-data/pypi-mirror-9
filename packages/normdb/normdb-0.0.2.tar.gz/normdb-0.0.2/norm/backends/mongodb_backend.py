"""Simple DBM interface for norm."""

import pymongo
import norm.framework


@norm.framework.store
class MongoDBStore(object):

    def __init__(self, database):
        self._database = database

    @norm.framework.deserialize
    def fetch(self, model, key):
        collection = self._database[_to_model_name(model)]
        result = collection.find_one({"_id": key})
        if result:
            result = model.from_dict(result)
        return result

    @norm.framework.serialize
    def save(self, instance):
        collection = self._database[_to_model_name(instance.__class__)]
        identifier = instance.identify()
        data = instance.to_dict()
        if identifier:
            data.setdefault("_id", identifier)
        new_identifier = collection.save(data, safe=True)
        instance.identify(new_identifier)

    @norm.framework.deserialize
    def create(self, model, **kwargs):
        instance = model(**kwargs)
        self.save(instance)
        return instance

    @norm.framework.deserialize
    def find(self, model, query=None):
        query = query or {}
        collection = self._database[_to_model_name(model)]
        for result in collection.find(query):
            yield model.from_dict(result)


def _to_model_name(model):
    return model.__name__.lower()


@norm.framework.connection
class MongoDBConnection(object):

    @classmethod
    def from_uri(cls, uri):
        database = uri.split("/")[-1]
        return cls(uri, database)

    def __init__(self, uri, database):
        self._uri = uri
        self._client = pymongo.MongoClient(uri)
        self._database = database

    def disconnect(self):
        self._client.close()

    def get_store(self):
        return MongoDBStore(self._client[self._database])


def register(context):
    context.register_connection("mongodb", MongoDBConnection)
