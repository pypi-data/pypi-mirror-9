import base64
import logging
import json

import requests
from pprint import pformat
from django.conf import settings
from django.utils.translation import ugettext as _


default_facet_mode = getattr(settings, "STUDIOGDO_FACET_MODE", "dom5")


class StudiogdoApi(object):
    """
    Rest API to retrieve objects in a hierarchical back-end
    """

    # Studiogdo URL root
    DEFAULT_ROOT = "http://%s/%s" % (settings.STUDIOGDO_HOST,
                                     settings.STUDIOGDO_SERVLET)

    # Default facet mode
    DEFAULT_MODE = 'django'

    def __init__(self, root_address=DEFAULT_ROOT, options=None, cookies=None):
        self.root_address = root_address

        self.options = getattr(settings, 'STUDIOGDO_OPTIONS', {})
        if options is not None:
            self.options.update(options)
        self.params = {}

        # cookies from django
        self.cookies = cookies or {}

        # cookies from studiogdo (will be added to cookies on next call)
        self.studiogdo_cookies = {}

        self.log = logging.getLogger("studiogdo")

    def append_param(self, param, value):
        self.params[param] = value


    @property
    def decoded_params(self):
        """ decode self params so that a human can read them """
        decoded_params = {}
        for k, v in self.params.iteritems():
            key, value = (k, v[0] if isinstance(v, list) else v)
            try:
                name_sep_index = k.find('_')
                if name_sep_index >= 0:
                    key = k[:name_sep_index + 1] + base64.b64decode(k[name_sep_index + 1:])
                    if k[:1] == 'p':  # in case of a plugged parameter, value has to be decoded too
                            value = base64.b64decode(value)
                if k in {'ap', 'ak1'}:
                    value = base64.b64decode(value)
            except:
                pass  # don't bother decoding path if it is not decodable
            finally:
                decoded_params[key] = value
        return decoded_params

    #
    # HTML FACET
    #
    # Path are encoded
    #

    def get_empty(self):
        """ Empty RPC entry to retrieve tomcat cookie. """
        return self.send('get', 'empty.gdo')

    def disconnect(self):
        """ Disconnect user connected."""
        return self.send('get', 'disconnect.gdo')

    def get_prop(self, path):
        """ Simple get RPC entry to retrieve a property value. """
        if path:
            self.append_param("ap", path)
        return self.send('get', 'prop.gdo')

    def post_empty(self, path=None, form_data=None):
        if path:
            self.append_param("ap", path)
        return self.send("post", "empty.gdo", form_data)

    def _post_facet(self, cmd, path, skeleton, facet="html5", form_data=None):
        if path:
            self.append_param("ap", path)
        self.append_param("m", skeleton)
        self.append_param("f", facet if facet else StudiogdoApi.DEFAULT_MODE)
        return self.send('post', "%s.gdo" % cmd, form_data)

    def post_facet(self, path, skeleton, facet="html5", form_data=None):
        return self._post_facet('facet', path, skeleton, facet, form_data)

    def post_facets(self, path, skeleton, facet="html5", form_data=None):
        return self._post_facet('facets', path, skeleton, facet, form_data)

    def apply_command(self, path, command, form_data=None):
        if path:
            self.append_param("ap", path)
        self.append_param("c", command)
        return self.send('post', "apply.gdo", form_data)

    #
    # PYTHON FACET
    #
    #   Path are not encoded
    #

    def get_list(self, path, slot, attrs=None, tid=None):

        # import ipdb; ipdb.set_trace()
        if settings.STUDIOGDO_DEBUG:
            self.log.debug("path:%s, slot:%s, attrs:%s", path, slot, attrs)

        if path:
            self.append_param("p", path)
        if tid:
            self.append_param("tid", tid)
        _list = '[%s]' % ', '.join("\'%s\'" % a for a in attrs)
        _list = _list.replace('\'{', '{')
        _list = _list.replace('}\'', '}')
        self.append_param("m", '{"data-path":%s, "data-value":%s}' % (slot, _list))
        self.append_param("f", "python")
        response = self.send('get', 'facet.gdo')
        if response.content.find("JsonParseException") != -1:
            raise Exception(response.content)
        return response

    #
    #   PYTHON INTERFACE
    #

    def send(self, method, url, data=None, content_type='application/x-www-form-urlencoded;charset=UTF-8', files=None):
        """ Return the studiogdo cookies, the XML result of a studiogdo call."""

        headers = {
            "content-type": content_type
        }

        request_kwargs = {
            'url': '%s/%s' % (self.root_address, url),
            'headers': headers,
        }

        # multipart
        if content_type is None:
            request_kwargs = {'url': '%s/%s' % (self.root_address, url)}

        # add studiogdo cookies
        if self.cookies:
            request_kwargs['cookies'] = self.cookies

        # set default options in parameters
        self.params.update(self.options)
        if "acceptNoStencil" not in self.params:
            self.append_param("acceptNoStencil", "true" if settings.STUDIOGDO_DEBUG else "false")
        if "country" not in self.params:
            country = getattr(settings, "STUDIOGDO_COUNTRY", None)
            if country:
                self.append_param("country", country)
        # set data in parameters
        data = data or {}
        self.params.update(data)
        data_name = "data" if method.lower() == "post" else "params"
        request_kwargs[data_name] = self.params
        if files:
            request_kwargs["files"] = files
        # request_kwargs["data"] = self.params
        # request_kwargs["params"] = self.params

        try:
            response = getattr(requests, method)(**request_kwargs)
        except:
            raise Exception("studiogdo service not available (url: %s)" % request_kwargs['url'])

        if not response.ok:
            try:
                reason = u"%s" % response.content
            except UnicodeDecodeError:
                reason = u"%s - ISO-8859-1" % response.reason.decode("ISO-8859-1")
            error = u"studiogdo error (code: %s, url: %s) : %s" % (response.status_code, request_kwargs['url'], reason)
            params = pformat(self.decoded_params, indent=2)
            raise Exception("\n".join([error.encode("utf8"),params]))
        elif url == "apply.gdo" and default_facet_mode == "trans":
            if response.content:
                content = json.loads(response.content)
                for k,v in content.iteritems():
                    if isinstance(v, list):
                        content[k] = [_(vi) for vi in v]
                    elif isinstance(v, basestring) and not v.isdigit():
                        content[k] = [_(vi) for vi in v]
                else:
                    response._content = json.dumps(content)

        # reset params for next call
        self.params = {}

        # memorize the cookie for several studiogdo calls in same request
        if response.cookies:
            self.cookies = response.cookies
            self.studiogdo_cookies = response.cookies

        return response
