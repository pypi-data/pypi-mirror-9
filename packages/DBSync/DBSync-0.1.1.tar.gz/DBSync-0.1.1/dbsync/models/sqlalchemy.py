# -*- coding:utf-8 -*-
__author__ = 'nathan'

try:
    import cPickle as pickle
except ImportError:  # pragma: nocover
    import pickle

try:
    from sqlalchemy import create_engine, Table, Column, MetaData, Unicode, Float, LargeBinary, select
    from sqlalchemy.exc import IntegrityError
except ImportError:  # pragma: nocover
    raise ImportError('SQLAlchemyJobStore requires SQLAlchemy installed')

from dbsync.models.base import SyncBaseModel

class SQLAlchemyModel(SyncBaseModel, Table):
    pass