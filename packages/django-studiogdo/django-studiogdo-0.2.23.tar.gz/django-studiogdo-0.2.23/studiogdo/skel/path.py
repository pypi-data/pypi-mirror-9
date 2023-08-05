from itertools import ifilterfalse
import os
from django.core.exceptions import SuspiciousOperation


def compose_path(*args):
    iter = ifilterfalse(lambda x: x is None, args)       # removes empty pathes
    path = os.path.normpath(os.path.join(*iter))
    if path.startswith(".."):
        raise SuspiciousOperation(".. in %s not allowed" % path)
    return path
