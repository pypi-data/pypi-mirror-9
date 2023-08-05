import datetime

try:
    import simplejson as json
except ImportError:
    import json


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.date):
            return obj.isoformat()

        if isinstance(obj, datetime.datetime):
            return obj.isoformat()

        if isinstance(obj, dict):
            return '\n'.join([u'%s: %s' % (k, v) for k, v in obj.iteritems()])

        return json.JSONEncoder.default(self, obj)
