# -*- coding:utf-8 -*-
__author__ = 'nathan'

try:
    import cPickle as pickle
except ImportError:  # pragma: nocover
    import pickle

try:
    from bson.binary import Binary
    from pymongo.errors import DuplicateKeyError
    from pymongo import MongoClient, ASCENDING
except ImportError:  # pragma: nocover
    raise ImportError('MongoDBModel requires PyMongo installed')

try:
    from mongoengine.document import Document
    from mongoengine.errors import ValidationError
except ImportError:  # pragma: nocover
    raise ImportError('MongoDBModel requires mongoengine installed')

from dbsync.models.base import SyncBaseModel

class MongoDBModel(SyncBaseModel, Document):

    def __init__(self):
        pass