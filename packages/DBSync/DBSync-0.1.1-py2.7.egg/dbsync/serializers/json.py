# -*- coding:utf-8 -*-
__author__ = 'nathan'

import json
from datetime import date, datetime

from dbsync.serializers.base import BaseSerializer

class JSONSerializer(BaseSerializer):
    """ serialize model to json """

    def serialize(self, model, ensure_ascii=True, cls=DatetimeJSONEncoder):
        """

        :param model:
        :param ensure_ascii: boolean, default True, see alse json.dumps()
        :param cls:
        :return:
        """
        return json.dumps(model, ensure_ascii, cls)


class DatetimeJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)