from toolz import memoize

class _S3(object):
    pass


def S3(cls):
    """ Parametrized Chunks Class """
    return type('S3(%s)' % cls.__name__, (cls, _S3), {'subtype': cls})

S3 = memoize(S3)
