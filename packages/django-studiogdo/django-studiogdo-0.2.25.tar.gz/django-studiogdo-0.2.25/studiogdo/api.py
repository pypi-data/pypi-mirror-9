import base64
import logging

import requests
from django.conf import settings


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
        if hasattr(settings, 'STUDIOGDO_OPTIONS'):
            self.options = settings.STUDIOGDO_OPTIONS
        else:
            self.options = {}
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
            self.append_param("ap", path)
        if tid:
            self.append_param("tid", tid)
        _list = '[%s]' % ', '.join("\'%s\'" % a for a in attrs)
        self.append_param("m", '{"data-path":"%s", "data-value":%s}' % (slot, _list))
        self.append_param("f", "python")
        response = self.send('get', 'facet.gdo')
        if response.content.find("JsonParseException") != -1:
            raise Exception(response.content)
        return response

    #
    #   PYTHON INTERFACE
    #

    def send(self, method, url, data=None,
             content_type='application/x-www-form-urlencoded;charset=UTF-8', files=None):
        """ Return the studiogdo cookies, the XML result of a studiogdo call."""

        headers = {"content-type": content_type}

        request_kwargs = {'url': '%s/%s' % (self.root_address, url),
                          'headers': headers}

        # multipart
        if content_type is None:
            request_kwargs = {'url': '%s/%s' % (self.root_address, url)}


        # add studiogdo cookies
        if self.cookies:
            request_kwargs['cookies'] = self.cookies

        # set default options in parameters
        self.params.update(self.options)
        self.append_param("acceptNoStencil", "true" if settings.STUDIOGDO_DEBUG else "false")

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
            raise Exception("studiogdo service not available (%s)" % request_kwargs['url'])

        if not response.ok:
            raise Exception("studiogdo error (code: %s, url: %s) : %s" % (response.status_code, request_kwargs['url'], response.reason))

        # reset params for next call
        self.params = {}

        # memorize the cookie for several studiogdo calls in same request
        if response.cookies:
            self.cookies = response.cookies
            self.studiogdo_cookies = response.cookies

        return response
