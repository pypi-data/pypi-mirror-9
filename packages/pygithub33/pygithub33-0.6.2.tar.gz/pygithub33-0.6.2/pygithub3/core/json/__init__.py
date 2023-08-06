# -*- coding: utf-8 -*-
"""
Emulate json module with encode/decoders to support github datetime format
"""

from datetime import datetime
try:
    import simplejson as json
except ImportError:
    import json

import six

GITHUB_DATE_FORMAT = '%Y-%m-%dT%H:%M:%SZ'


class GHJSONEncoder(json.JSONEncoder):
    def default(self, o):
        try:
            return datetime.strftime(o, GITHUB_DATE_FORMAT)
        except:
            return super(GHJSONEncoder, self).default(o)


def gh_decoder_hook(dict_):
    for k, v in six.iteritems(dict_):
        try:
            date = datetime.strptime(v, GITHUB_DATE_FORMAT)
            dict_[k] = date
        except:
            continue
    return dict_


def dumps(obj, cls=GHJSONEncoder, **kwargs):
    return json.dumps(obj, cls=cls, **kwargs)


def loads(s, object_hook=gh_decoder_hook, **kwargs):
    if type(s) is six.binary_type:
        # XXX(Kagami): json module from python3 can't load bytes while
        # json from python2 can work with both str and unicode. Better
        # to get only unicode in this function but let's go this hack
        # for the time being. Seems like upstream bug:
        # <https://bugs.python.org/issue10976>.
        s = s.decode('utf-8')
    return json.loads(s, object_hook=object_hook, **kwargs)

dump = json.dump
load = json.load
