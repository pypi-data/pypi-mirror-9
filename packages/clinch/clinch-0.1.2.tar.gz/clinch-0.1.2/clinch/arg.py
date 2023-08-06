class Argument(object):
    def __init__(self, *names, **kwargs):
        assert len(names) > 0
        assert 'dest' not in kwargs, \
            'dest is implicitly set to the argument name'

        self.names = names
        self.kwargs = kwargs

    @property
    def is_option(self):
        return any(name.startswith('-') for name in self.names)

    def __repr__(self):
        parts = (
            ['%s' % name for name in self.names] +
            ['%s=%r' % (k, v) for k, v in self.kwargs.iteritems()]
        )

        return '%s(%s)' % (type(self).__name__, ', '.join(parts))
