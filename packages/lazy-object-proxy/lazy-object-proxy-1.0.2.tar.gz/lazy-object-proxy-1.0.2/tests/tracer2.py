class T(object):
    __slots__ = ()

    @property
    def __dict__(self):
        return {'foo': 'bar'}



