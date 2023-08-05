# -*- coding: utf-8 -*-
import re
from collections import OrderedDict


def path(exp, skel, context=None, template_name=None):
    context = context or {}
    reg = re.compile(r'%s' % (exp,))
    if isinstance(skel, basestring):
        skel = [skel]
    return (reg, {"skel": skel, "context": context, "template_name": template_name})


class Patterns(object):
    def __init__(self, *kwargs):
        self._regexes = OrderedDict()
        for elt in kwargs:
            self._regexes[elt[0]] = elt[1]

    def __getitem__(self, name):
        # on rajoute dans le skel_dict les variables du regexp du path
        for regex, path_dict in self._regexes.items():
            m = regex.match(name)
            if m:
                path_group = m.groupdict()
                path_dict_return = path_dict.copy()
                path_dict_return.update({"path_group": path_group})
                return path_dict_return
        raise KeyError('Key %s does not match any regex' % name)

    def iterkeys(self):
        return self._regexes.iterkeys()

    def iteritems(self):
        return self._regexes.iteritems()

    def keys(self):
        return [reg.pattern for reg in self._regexes.iterkeys()]


patterns = Patterns
