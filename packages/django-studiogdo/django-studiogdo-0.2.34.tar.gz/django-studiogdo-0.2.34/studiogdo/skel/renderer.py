# -*- coding: utf-8 -*-

import re
import sys
import itertools
import json
import time
from base64 import b64encode as encode
from pprint import PrettyPrinter

import ipdb  # not really pythonic but veryusefull...
from bs4 import BeautifulSoup, NavigableString, Tag
from django.conf import settings

from path import compose_path


COND_REGEXP = re.compile(r"^(?P<value>[^!=<>]*)(?P<oper>(!|[!=<>]=?)?)(?P<slot>[^!=<>]*)$")

STRING_FORMAT = re.compile(r"^s(?P<value>(\[\])?)(?P<filter>[ulcw])?$")
INTEGER_FORMAT = re.compile(r"^i((\*(?P<mult>(\d)*))|(\/(?P<div>(\d)*)))?(?P<sep>[.,])?(?P<dec>\#*)(?P<unit>[^?]*)(?P<nothing>\??)$")
DATE_FORMAT = re.compile(r"^dt_(?P<exp>.*)$")

input_tags = ["input", "textarea"]
final_tags = ["img", "meter", "progress"]
container_tags = ["a", "abbr", "address", "article", "aside", "button", "blockquote",
                  "caption", "div", "fieldset", "figcaption", "footer", "form", "legend",
                  "h1", "h2", "h3", "h4", "h5", "h6", "header", "hgroup", "label", "nav", "p",
                  "pre", "span", "section", "tbody", "tr", "td", "thead", "tfoot",
]
list_tags = ["ul", "ol"]

iterator_tags = ["tr", "li", "option", "section"]


class SoupWrapper(object):
    def __init__(self):
        self.soup = []  # last document parsed on top

    def is_input(self, elt):
        """ Return True if the element is an input element """
        return elt.name in input_tags

    def is_container(self, elt):
        return elt.name in container_tags

    def get_children(self, elt):
        for child in (child for child in elt.children if isinstance(child, Tag)):
            yield child

    def get_immutable_children(self, elt):
        return [x for x in elt.children if isinstance(x, Tag)]

    def _insert_elt(self, elt, parent=None, before=None):
        if parent and before:
            raise Exception("cannot insert element with parent %s and sibling %s" % (parent, before))

        if before:
            before.insert_before(elt)
        elif parent:
            parent.append(elt)

    def append_new_tag(self, tag, parent=None, before=None):
        elt = self.soup[-1].new_tag(tag)
        self._insert_elt(elt, parent, before)
        return elt

    def clone_tag(self, elt, parent=None, before=None):

        # string case
        if isinstance(elt, NavigableString):
            string = type(elt)(elt)
            self._insert_elt(string, parent, before)
            return string

        # clone the element
        clone = Tag(None, elt.builder, elt.name, elt.namespace, elt.nsprefix)
        self._insert_elt(clone, parent, before)

        # work around bug where there is no builder set
        # https://bugs.launchpad.net/beautifulsoup/+bug/1307471
        clone.attrs = dict(elt.attrs)
        for attr in ('can_be_empty_element', 'hidden'):
            setattr(clone, attr, getattr(elt, attr))
        for child in elt.contents:
            self.clone_tag(child, parent=clone)
        return clone


class HTMLParser(object):
    def get_data_path(self, elt, attr='data-path'):
        """ Return path and True if operator not was found """
        path = elt.get(attr, ".")
        if path == ".":
            return ""

        if path:
            m = COND_REGEXP.match(path)
            if m:
                slot = m.group('slot') if m.group('oper') else m.group('value')
                if attr == 'data-path' and m.group('oper') == '!':
                    if self.strict:
                        raise Exception("not condition %s in path %s" % (path, elt))
                    elt["data-cond"] = path
                    del elt["data-path"]
                path = slot
        return path

    def get_all_pathes(self, elt, container='', exclude={}):
        """ Return all pathes used from a simple element """

        # search path used in attributes
        pathes = set()
        for k, v in elt.attrs.iteritems():
            if k in exclude:
                continue

            if v:

                # search from data-path
                if (k == "data-path" or k == "data-cond"):
                    path = self.get_data_path(elt, k)
                    pathes.add(compose_path(path, container))

                # search from data-value
                elif k in ["data-value", "data-label"]:
                    pourcent = v.find('%')
                    v = v if pourcent == -1 else v[:pourcent]
                    pathes.add(v)

                elif len(k) > 9 and k.startswith("data-prop"):
                    pourcent = v.find('%')
                    v = v if pourcent == -1 else v[:pourcent]
                    pathes.add(v)

                elif len(k) > 9 and k.startswith("data-text") or k.startswith("data-html"):
                    soup = BeautifulSoup(v, "html5")
                    p = self.get_all_pathes_recursiv(soup.body, container=container)
                    pathes.update(p)

        return pathes

    def get_all_pathes_recursiv(self, *args, **kwargs):
        """ Return all pathes used from an element and its children"""

        pathes = set()
        container = kwargs.get("container", "")
        for elt in (elt for elt in itertools.chain(*args) if isinstance(elt, Tag)):
            data_path = self.get_data_path(elt)

            # iterator tag with data-path are not in same scope
            if elt.name in iterator_tags:

                # specific case where tr is in tbody (data_path is then previous tr in thead)
                if elt.name == 'tr' and not data_path:
                    if elt.parent.name == "tbody":
                        thead = elt.parent.parent.thead
                        trs = thead.find_all("tr")
                        data_path = self.get_data_path(trs[0])

                # creates iterator path
                iterator_path = compose_path(container, data_path)
                props = self.get_all_pathes(elt, container=compose_path(container, data_path), exclude={'data-path'})
                new_props = self.get_all_pathes_recursiv(elt)  # pathes in iterator are relatives (no container)
                iterator_props = props.union(new_props)
                iterator = PathIterator(iterator_path, iterator_props)
                iterator.add_in(pathes)
                continue

            # add pathes from element
            for path in self.get_all_pathes(elt):
                pathes.add(compose_path(container, path))

            # search in children (data-path is used but not on first call)
            new_container = container
            if data_path and data_path != ".":
                new_container = compose_path(container, data_path)
                pathes.add(new_container)
            new_props = self.get_all_pathes_recursiv(self.get_children(elt), container=new_container)
            PathIterator.update(pathes, new_props)

        return pathes


    def get_value_path(self, elt, attr="data-value", path=None):
        """ Return value path and value format """
        path = path or elt.get(attr, "")
        index = path.find("%")

        # if no format defined, then use string format
        if index == -1:
            return path, "s"
        return path[:index], path[index + 1:]


class StudiogdoWrapper(object):
    def is_empty(self, stcl, slot):
        """ Test if a slot is empty """

        if not slot:
            raise Exception("is_empty : the property path should not be null")

        # get from stencil
        return stcl.get(slot) is None

    def get_value(self, stcl, path, _format="s", alert=True):
        """ Return property value and property path """

        if not path:
            raise Exception("get_value : the property path should not be null")

        if path.endswith("^"):
            prop = path[:-1]
            value_path = compose_path(stcl.get("data-path", ""), prop)
            value = encode(value_path)
            return self.format_value(value, _format)

        # if value is already stored
        value = stcl.get(path)
        if value is not None:
            return self.format_value(value, _format)
        composed = compose_path(stcl.get("data-path", ""), path)
        value = stcl.get(composed)
        if value is not None:
            return self.format_value(value, _format)

        if self.strict and alert:
            pp = PrettyPrinter()
            msg = 'get_value : %s not in stcl (%s)' % (path, pp.pformat(stcl))
            raise Exception(msg)

        return None

    def format_value(self, value, _format):

        found = STRING_FORMAT.search(_format)
        if found:
            if not value:
                return ""

            _filter = found.group('filter')
            if _filter:
                if _filter == 'u':
                    return value.upper()
                if _filter == 'l':
                    return value.lower()
                if _filter == 'c':
                    return value.capitalize()
            return value

        found = INTEGER_FORMAT.search(_format)
        if found:
            parsed = False

            if not value:
                nothing = found.group('nothing')
                if nothing:
                    return ""
                return 0

            mult = found.group('mult')
            if mult:
                parsed = True
                value = str(int(value) * int(mult))
            div = found.group('div')
            if div:
                parsed = True
                value = str(int(value) / int(div))
            dec = found.group('dec')
            if dec:
                parsed = True
                f = "%%.%sf" % (len(dec),)
                value = f % float(value)
            sep = found.group('sep')
            if sep:
                value = value.replace('.', sep)
            unit = found.group('unit')
            if unit:
                value = value + unit

            return value if parsed else str(int(value))

        found = DATE_FORMAT.search(_format)
        if found:
            if not value:
                return ""

            try:
                exp = found.group("exp")
                exp = exp.replace("dd", "%d")
                exp = exp.replace("MM", "%m")
                exp = exp.replace("yyyy", "%Y")
                exp = exp.replace("yyyy", "%Y")
                exp = exp.replace("hh", "%H")
                exp = exp.replace("mm", "%M")
                has_date = value.find('-') != -1
                has_time = value.find(':') != -1
                if has_date and has_time:
                    t = time.strptime(value, "%Y-%m-%d %H:%M")
                elif has_date:
                    t = time.strptime(value, "%Y-%m-%d")
                elif has_time:
                    t = time.strptime(value, "%H:%M:%S")
                return time.strftime(exp, t)
            except ValueError as e:
                return str(e)

        return value


class HTMLRenderer(SoupWrapper, HTMLParser, StudiogdoWrapper):
    TRANSACTION_ID = 0

    def __init__(self, api, mode="html", debug=settings.STUDIOGDO_DEBUG, strict=not settings.STUDIOGDO_DEBUG):
        self.api = api
        self.debug = debug
        self.lists = {}
        self.mode = mode
        self.strict = strict
        HTMLRenderer.TRANSACTION_ID = HTMLRenderer.TRANSACTION_ID + 1

        SoupWrapper.__init__(self)

    def extract_pathes(self, skel):
        soup = BeautifulSoup(skel, "html5")
        return self.get_all_pathes_recursiv(soup.body.children)


    def render(self, path, skel, mode=None, stcl=None):
        """
        Returns the skeleton completed.
        Accepted mode: text et html
        """
        soup = BeautifulSoup(skel, "html5")
        self.soup.append(soup)

        body = soup.body
        if not stcl:
            stcl = {"data-path": path, ".": path}
            stcl = self.get_stencil(stcl, path, body)
        self.expand_children(stcl, body)

        mode = mode or self.mode
        if mode == "html":
            result = u''.join((unicode(c) for c in body.contents))
        if mode == "text":
            result = body.get_text(strip=True)

        self.soup.pop()
        return result

    def expand(self, stcl, elt):
        """
        A stencil is a dict with at least a data-path entry
        """

        # debug infos
        if self.debug:
            elt["debug"] = "pass"
            debug = elt.get("data-debug")
            if settings.STUDIOGDO_DEBUG and debug == "stop":
                ipdb.set_trace()

        # check condition
        if not self.satisfy_condition(stcl, elt):
            elt.decompose()
            return
        self.expand_attributes(stcl, elt)

        # expand from type
        if self.is_container(elt):
            decomposed = self.expand_container(stcl, elt)
            if decomposed:
                return
        elif elt.name in final_tags:
            self.expand_final(stcl, elt)
        elif self.is_input(elt):
            self.expand_input(stcl, elt)
        elif elt.name in ["select"]:
            self.expand_select(stcl, elt)
        elif elt.name in list_tags:
            self.expand_list(stcl, elt)
        elif elt.name in ["table"]:
            self.expand_table(stcl, elt)

        self.remove_path(elt)

    def expand_children(self, stcl, elt):
        for child in self.get_children(elt):
            self.expand(stcl, child)

    def expand_container(self, stcl, container):
        """ Returns True if the container is decomposed """
        path = self.get_data_path(container)
        if path:

            # expand children
            empty = self.is_empty(stcl, path)
            if not empty:
                new_stencil = self.get_stencil(stcl, path, container)
                self.expand_children(new_stencil, container)
                self._set_final_value(stcl, container)
            else:
                container.decompose()
            return True
        else:
            self.expand_children(stcl, container)
            self._set_final_value(stcl, container)
        return False

    def expand_final(self, stcl, final):
        self._set_final_value(stcl, final)

    def _set_final_value(self, stcl, final):

        # expand to text value
        value_path, _format = self.get_value_path(final)
        if value_path:
            value = self.get_value(stcl, value_path, _format)
            if value:
                span = self.append_new_tag("span", final)
                span.append(value)
                path = self.get_data_path(final)
                self.set_data_path(span, compose_path(path, value_path))

    def expand_select(self, stcl, select):

        def set_selected(elt, value, by_value, multiple=False):
            """ set selected option """
            if value:
                for option in elt.find_all("option"):
                    if by_value:
                        selected = option["value"]
                    else:
                        selected = option.string
                    if value == selected:
                        option["selected"] = "selected"
                        if not multiple:
                            break

        # replace by generated options
        for child in self.get_immutable_children(select):

            # check condition
            if not self.satisfy_condition(stcl, child):
                child.decompose()
                continue
            self.expand_attributes(stcl, child)

            # expand child
            if child.name == "option":
                self._expand_option(stcl, select, child)

        # the selected stencil is a property
        value_path, _format = self.get_value_path(select)
        label_path = select.get("data-label")

        # get value for label (label may be different as value)
        path = self.get_data_path(select)
        p = compose_path(path, label_path if label_path else value_path)
        value = self.get_value(stcl, p, _format)

        # set post parameter
        name = select.get('name', "%s_" % _format if _format else "s_")
        select["name"] = name + encode(stcl.get("data-path", ""))

        # comparaison mode
        by_value = False if label_path else True

        # multiple selections
        if name.startswith("m_"):
            for v in value.split(':'):
                set_selected(select, v, by_value, multiple=True)

        # single selection
        else:
            set_selected(select, value, by_value)

    def _expand_option(self, stcl, select, option):

        path = self.get_data_path(option)
        value_path, value_format = self.get_value_path(option)
        label_path, label_format = self.get_value_path(option, attr="data-label")

        # the options are not generated from the stencil
        if not path:

            # if value path defined, then changes label and value
            if value_path:
                self._complete_option(stcl, value_path, value_format, label_path, label_format, option)

        # the options are generated
        else:

            # iterates over data-path of the option
            props = [value_path, label_path]
            stencils = self.get_list(stcl, path, props)
            try:
                for s in json.loads(stencils.content).get("data-value"):
                    opt = self.append_new_tag("option", before=option)
                    self._complete_option(s, value_path, value_format, label_path, label_format, opt)
            except Exception as e:
                traceback = sys.exc_info()[2]
                msg = "Error: %s[%s], %s" % (e, traceback.tb_lineno, stencils.content)
                raise Exception(msg)

            # remove option template
            option.decompose()

    def _complete_option(self, stcl, value_path, value_format, label_path, label_format, option):
        """ Complete option element """

        # expand attributes
        self.expand_attributes(stcl, option)

        # set label and value
        if label_path:
            option.string = self.get_value(stcl, label_path, label_path)
        else:
            option.string = self.get_value(stcl, value_path, value_format)
        option["value"] = self.get_value(stcl, value_path, value_format)

    def expand_list(self, stcl, elt):

        # expands all items
        for child in self.get_immutable_children(elt):

            # only take first li elements
            if child.name.lower() != "li":
                self.expand(stcl, child)
                continue

            # iterates over data-path of the list
            value_path, _ = self.get_value_path(child)
            if not value_path:
                self.expand_children(stcl, child)
                continue

            props = [value_path]
            path = self.get_data_path(child)
            stencils = self.get_list(stcl, path, props)
            try:
                for s in json.loads(stencils.content).get("data-value"):
                    # check condition
                    li = self.clone_tag(child, before=child)
                    self.expand_attributes(stcl, li)
                    self._set_final_value(s, li)
                    self.expand_children(s, li)
            except Exception as e:
                traceback = sys.exc_info()[2]
                msg = "Error: %s[%s], %s" % (e, traceback.tb_lineno, stencils.content)
                raise Exception(msg)

            child.decompose()

    def expand_table(self, stcl, table):
        thead = table.thead
        if thead:
            return self.expand_one_dimension_table(stcl, table)
        else:
            # pivot table as two dimension table;
            pass

    def expand_one_dimension_table(self, stcl, table):

        # the last tr in thead serve as a template for each row
        thead = table.thead
        trs = thead.find_all("tr")
        if not trs:
            self.expand_children(stcl, table)
            return

        # last tr in header must have a path attribute
        thr = trs[-1]
        pr = self.get_data_path(thr)

        # simple tr (not as iterator)
        if not pr:
            self.expand_children(stcl, table)
            return

        # complete others elements in table
        for elt in self.get_children(table):
            if not (elt.name.lower() == "thead" or elt.name.lower() == "tbody"):
                self.expand(stcl, elt)

        # tr in body may serve as template
        thh = thr.find_all("th")
        tbody = table.tbody
        tbr = tbody.tr if tbody else []
        tbd = tbr.find_all("td") if tbr else []

        # create tbody if doesn't exists
        if not tbody:
            tbody = self.append_new_tag("tbody", parent=table)

        # creates a row for each stencil
        props = self.get_all_pathes_recursiv(thh, tbd)
        stencils = self.get_list(stcl, pr, props)
        try:
            content = stencils.content
            if content:
                for s in json.loads(content).get("data-value"):
                    s[".."] = stcl
                    ntr = self.append_new_tag("tr", parent=tbody)
                    self.set_data_path(ntr, s.get("data-path"))
                    src = tbr if tbr else thr
                    for key in (key for key in src.attrs if not key == "data-path"):
                        ntr[key] = src.attrs[key]
                    self.expand_attributes(s, ntr)

                    # for each column declared in the header
                    tbdIndex = 0
                    for th in thh:
                        value_path, _format = self.get_value_path(th)

                        # create td from template
                        if self.td_from_header(th):
                            td = self.append_new_tag("td", parent=ntr)

                            # adds attributes and data class
                            # copyAndExpandAttributes(stclContext, s, th, td);
                            # String classPath = th.attr(CLASS_ATTRIBUTE);
                            # addClassToElement(stclContext, s, td, classPath);

                            # expands container associated for each row (only if
                            # data-path
                            # defined)
                            # others children (note relative to path) stay in header
                            for f in th.select("[data-path]"):
                                if self.is_container(f):
                                    ff = self.clone_tag(f, parent=td)
                                    self.expand(s, ff)

                        # td are defined in body (no content from stencil)
                        else:
                            if tbd and len(tbd) > tbdIndex:
                                td = self.clone_tag(tbd[tbdIndex], parent=ntr)
                                tbdIndex = tbdIndex + 1
                                # value_path, _format = self.get_value_path(td)
                                # expandAttributes(stclContext, s, td);
                            else:
                                td = self.append_new_tag("td", parent=ntr)

                        # adds cell content
                        if self.td_from_header(th):

                            # uses label for content (value can also be used)
                            if value_path and not value_path.startswith("!"):
                                value = self.get_value(s, value_path, _format)
                                td.string = unicode(value)
                        else:
                            td["data-path"] = "."
                            self.expand_container(s, td)

                            # add apath
                            # apath = compose(pwd, valuePath)
                            # setDataAPath(stclContext, td, apath)
        except ValueError as e:
            parent = table.parent
            span = self.append_new_tag("span", parent=parent)
            traceback = sys.exc_info()[2]
            span.append("Error: %s[%s], %s" % (e, traceback.tb_lineno, stencils.content))
            return

        # suppresses container with data-path from header (div, form)
        # (edit form should be first element)
        for th in thh:
            if self.td_from_header(th):
                for f in (f for f in th.select("[data-path]") if self.is_container(f)):
                    f.decompose()
            self.expand_children(stcl, th)

        # removes initial tbody content
        if tbr:
            tbr.decompose()

            # expands the tfoot if exists
            # Element tfoot = table.select("tfoot").first();
            # if (tfoot != null) {
            # completeChildren(stclContext, stcl, tfoot);
            # }

    def td_from_header(self, th):
        """ returns True is the tag has a value path or a label path """
        value_path = th.get("data-value")
        label_path = th.get("data-label")  # unusefull
        return value_path or label_path

    def expand_input(self, stcl, input):

        # expand to text value
        value_path, _format = self.get_value_path(input)
        if not value_path:
            return
        value = self.get_value(stcl, value_path, _format)

        # set value or select attribute
        tag = input.name.lower()
        if tag == "textarea":
            input["value"] = value
        elif tag == "input":
            _type = input.get('type')
            if _type == "checkbox":
                if value.lower() in ['true', '1', 'vrai', 'ok', 'o', 'oui']:
                    input["checked"] = "checked"
            elif _type == "radio":
                if value.lower() == input.get("value"):
                    input["checked"] = "checked"
            else:
                input["value"] = value

        # complete name with absolute path
        name = input.get('name')
        if not name:
            name = "%s_" % _format if _format else "s_"
        input["name"] = name + encode(compose_path(stcl.get("data-path"), value_path))

    def satisfy_condition(self, stcl, elt):
        cond = elt.get('data-cond')

        # check only if condition defined
        if not cond:
            return True

        # check comparision
        found = COND_REGEXP.search(cond)
        if found:
            value = found.group('value')
            oper = found.group('oper')
            slot = found.group('slot')

            # only slot name (value in value)
            if not slot:
                value = value if value else "."
                prop = self.get_value(stcl, value, _format="s", alert=False)
                if oper == "!":
                    return prop is None
                return prop is not None

            if oper == "!":
                prop = self.get_value(stcl, slot, _format="s", alert=False)
                return prop is None

            prop = self.get_value(stcl, slot, _format="s")
            return eval("'%s' %s '%s'" % (value, oper, prop))

        return False

    def expand_attributes(self, stcl, elt):
        """ Expand the element attributes """

        def set_attr(attr, value, sign):
            if value:
                if sign == "-":
                    elt[attr] = value
                else:  # sign == +
                    previous = elt.get(attr, "")
                    if type(previous) is list:
                        previous = ' '.join(previous)
                    elt[attr] = "%s %s" % (previous, value)

        # set path
        path = stcl.get("data-path")
        self.set_data_path(elt, path)

        # should be inlined here
        for key in [key for key in elt.attrs.keys() if len(key) > 9 and (key.startswith("data-prop") or key.startswith("data-text") or key.startswith("data-html"))]:
            sign = key[9]
            attr = key[10:]
            if key.startswith("data-prop"):
                value_path, _format = self.get_value_path(None, path=elt.attrs[key])
                value = self.get_value(stcl, value_path, _format)
            elif key.startswith("data-text"):
                value = self.render(path=None, skel=elt.attrs[key], mode="text", stcl=stcl)
            elif key.startswith("data-html"):
                value = self.render(path=None, skel=elt.attrs[key], mode="html", stcl=stcl)
            set_attr(attr, value, sign)
            del elt[key]

    def set_data_path(self, elt, path):
        """ Set element path attribute """

        if self.debug:
            elt['data-path-debug'] = path
        elt['data-apath'] = encode(path)

    def remove_path(self, elt):
        """ Remove all path attributes for security """
        del elt['data-path']
        del elt['data-value']
        del elt['data-label']
        del elt['data-cond']

    def get_list(self, stcl, path, props):
        data_path = stcl.get("data-path")
        key = "%s:%s:%s" % (data_path, path, props)

        # check not already called
        already = self.lists.get(key)
        if already:
            return already

        # store result
        stencils = self.api.get_list(data_path, path, props, tid=HTMLRenderer.TRANSACTION_ID)
        self.lists[key] = stencils
        return stencils

    def get_stencil(self, stcl, path, container):

        if self.debug:
            self.api.log.debug("get_stencil : from %s get %s in %s" % (stcl, path, container))

        # specific cases ("." may be not defined at root)
        if path == "." and stcl.get("."):
            return stcl

        # parent is defined only in case of included call
        if path == "..":
            return stcl.get("..")

        # get new stencil properties
        props = self.get_all_pathes_recursiv([container])
        if self.debug:
            self.api.log.debug("get_stencil : props are %s" % (props,))
        if props:
            values = self.get_list(stcl, path, props)
            try:
                content = values.content
                if content:
                    stencils = json.loads(content).get("data-value")
                    if self.debug:
                        self.api.log.debug("get_stencil : %s" % values.content)
                    return stencils[0]
                msg = 'get_stencil is empty'
                raise Exception(msg)
            except:
                msg = 'get_stencil : %s' % values.content
                raise Exception(msg)

        return stcl


class PathIterator:
    def __init__(self, path, props):
        self.path = path
        self.props = set(itertools.ifilter(lambda x: x != ".", props))

    def __str__(self):
        return self.path

    def __repr__(self):
        return '(' + self.path + ', [' + ', '.join(self.props) + '])'

    def __hash__(self):
        return hash(self.path)

    def __eq__(self, other):
        if isinstance(other, PathIterator):
            return other.path == self.path and other.props == self.props
        return False

    @staticmethod
    def update(pathes, other):
        for o in other:
            if isinstance(o, PathIterator):
                o.add_in(pathes)
            else:
                pathes.add(o)

    def add_in(self, pathes):
        iterator = itertools.ifilter(lambda x: isinstance(x, PathIterator) and x.path == self.path, pathes)
        try:
            iterator.next().props.update(self.props)
        except StopIteration:
            pathes.add(self)
