"""
switchboard.settings
~~~~~~~~~~~~~

:copyright: (c) 2012 Sourceforge.
:license: Apache License 2.0, see LICENSE for more details.
"""

NoValue = object()


class Settings(object):

    _state = {}

    @classmethod
    def init(cls, mongo_host='localhost', mongo_port=27017,
             mongo_db='switchboard', mongo_collection='switches',
             **kwargs):
        cls._state['SWITCHBOARD_MONGO_HOST'] = mongo_host
        cls._state['SWITCHBOARD_MONGO_PORT'] = mongo_port
        cls._state['SWITCHBOARD_MONGO_DB'] = mongo_db
        cls._state['SWITCHBOARD_MONGO_COLLECTION'] = mongo_collection
        remainder = kwargs.iteritems()
        remainder = [('SWITCHBOARD_%s' % k.upper(), v) for k, v in remainder]
        # convert timeouts to ints
        remainder = [(k, int(v) if k.endswith('TIMEOUT') else v)
                     for k, v in remainder]
        cls._state.update(dict(remainder))
        return cls()

    def __getattr__(self, name, default=NoValue):
        value = self._state.get(name, default)
        if value is NoValue:
            raise AttributeError
        return value

    def __delattr__(self, name):
        del self._state[name]

    def __setattr__(self, name, value):
        self._state[name] = value


settings = Settings.init()
