# -*- coding:utf-8 -*-
__author__ = 'nathan'

try:
    import cPickle as pickle
except ImportError:  # pragma: nocover
    import pickle

try:
    from peewee import *
except ImportError:  # pragma: nocover
    raise ImportError('PeeweeModel requires peewee installed')

from dbsync.models.base import SyncBaseModel

class PeeweeModel(SyncBaseModel, Model):

    def __init__(self):
        pass

    @classmethod
    def data_size(cls):
        """
        Total table size, query from table status
        :return:
        """
        return cls._status()["Data_length"]

    @classmethod
    def avg_row_size(cls):
        """
        avg size per row, query from table status
        :return:
        """
        return cls._status()["Avg_row_length"]

    @classmethod
    def row_count(cls):
        """
        query by count(*)
        :return:
        """
        return cls.raw('select * from (?)', (cls._meta.db_table))

    @classmethod
    def rows(cls):
        """
        query from table status
        :return:
        """
        return cls._status()["Rows"]

    # @cache_property
    @classmethod
    def _status(cls):
        return cls.raw('show table status like "(table_name)" ', (cls._meta.db_table)).dicts.execute()


