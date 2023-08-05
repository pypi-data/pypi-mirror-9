'''
Serialize data to/from foreign data types into python.
'''

from __future__ import print_function

import collections
import datetime
import dateutil.parser
import json
import re

Serializer = collections.namedtuple('Serializer', 'mime, encode, decode')


class DictResponse(dict):
    pass


class ListResponse(list):
    pass


class NormalJSONEncoder(json.JSONEncoder):
    """ Normal == iso datatime. """

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        else:
            return super(NormalJSONEncoder, self).default(obj)


class NormalJSONDecoder(json.JSONDecoder):
    """ Normal == iso datatime. """

    strict_iso_match = re.compile('\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}\:\d{2}.*)?$')

    def __init__(self):
        super(NormalJSONDecoder, self).__init__(object_hook=self.parse_object)

    def parse_object(self, data):
        """ Look for datetime looking strings. """
        for key, value in data.items():
            if isinstance(value, (str, type(u''))) and \
               self.strict_iso_match.match(value):
                data[key] = dateutil.parser.parse(value)
        return data

serializers = {
    'json': Serializer('application/json',
                       NormalJSONEncoder().encode,
                       NormalJSONDecoder().decode)
}
