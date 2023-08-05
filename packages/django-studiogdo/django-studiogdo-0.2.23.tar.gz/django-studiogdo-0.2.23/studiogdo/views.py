# -*- coding: utf-8 -*-

import re
import json
from base64 import b64decode

from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http.response import HttpResponse
from django.conf import settings

from studiogdo.api import StudiogdoApi


class SkelView(TemplateView):
    """
    skel should be defined or get_skel is then called (as template_name and get_template_name).
    """

    @property
    def skel(self):
        if not hasattr(self, "_skel"):
            self._skel = self.get_skel()
        return self._skel

    def get_skel(self):
        return self.data.get('m')

    def get_template_names(self):
        return self.skel;

    @property
    def data(self):
        if not hasattr(self, "_data"):
            self._data = getattr(self.request, self.request.method)
        return self._data

    def get_entry(self, **kwargs):
        return kwargs['entry']

    def get_facet(self):
        return self.data.get('f')

    def get_facet_mode(self):
        if isinstance(self.skel, list):
            skel = self.skel[0]
        else:
            skel = self.skel
        return 'json' if skel.endswith("jskel") else 'dom5'


    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        resp = None
        if settings.STUDIOGDO_FACET == "django":
            entry = self.get_entry(**kwargs)
            facet = self.get_facet()

            # django facet entry is not done on java
            if entry == "facet" and facet == StudiogdoApi.DEFAULT_MODE:
                entry = "empty"

            # should be optimized to be called only if needed
            api = request.studiogdo_api
            response = api.send(request.method.lower(), '%s.gdo' % entry, self.data)

            # on error 412 return error message
            if response.status_code == 412:
                valid = re.compile(r"<b>message</b> <u>([^<]*)</u>")
                se = valid.search(response.content)
                return HttpResponse(status=412, content=se.groups(0))

            content = response.content
            if response.status_code == 200:

                # django facet are rendered by django
                if facet == StudiogdoApi.DEFAULT_MODE:
                    skel = self.get(request, *args, **kwargs)
                    ap = self.data.get('ap')
                    renderer = request.html_renderer
                    content = renderer.render(b64decode(ap) if ap else "/", skel.render().content.decode('utf-8'))

                # if it'a a facet, we add a new attribute to the response
                elif facet == 'json' and response.content:
                    response.json = json.loads(response.content)
                elif facet == 'dom5':
                    response.html = response.content

            # create django response
            content_type = response.headers[
                'content-type'] if 'content-type' in response.headers else 'text/html; charset=utf-8'
            resp = HttpResponse(content=content, content_type=content_type,
                                status=response.status_code, reason=response.reason)

            for header, value in response.headers.iteritems():
                # if header in ['content-length', 'content-disposition']:
                if header in ['content-disposition']:
                    resp[header] = value

        elif settings.STUDIOGDO_FACET == "java":

            # if the request has a facet, get it as a template
            if self.data.get('f', None) == StudiogdoApi.DEFAULT_MODE:
                skel = self.get(request, *args, **kwargs)
                self.data['m'] = skel.render().content
                # check if skel extension is jskel for json or skel to html facet
                self.data['f'] = self.get_facet_mode()

            api = request.studiogdo_api
            entry = self.get_entry(**kwargs)
            if request.FILES:
                content_type = None
                files = {} # self.data.dict();
                for k,v in request.FILES.iteritems():
                    files[v.name] = v
                    # files[k] = (v.name, v, v.content_type)

            else:
                content_type = 'application/x-www-form-urlencoded;charset=UTF-8'
                files = None
            response = api.send(request.method.lower(), '%s.gdo' % entry, data=self.data.dict(), content_type=content_type, files=files)

            # on error 412 return error message
            if response.status_code == 412:
                valid = re.compile(r"<b>message</b> <u>([^<]*)</u>")
                se = valid.search(response.content)
                return HttpResponse(status=412, content=se.groups(0))

            if response.status_code == 200:

                # if it'a a facet, we add a new attribute to the response
                facet_mode = self.data.get('f', "")
                if facet_mode == 'json' and response.content:
                    response.json = json.loads(response.content)
                elif facet_mode == 'dom5':
                    response.html = response.content

            # create django response
            content_type = response.headers[
                'content-type'] if 'content-type' in response.headers else 'text/html; charset=utf-8'
            resp = HttpResponse(content=response.content, content_type=content_type,
                                status=response.status_code, reason=response.reason)

            for header, value in response.headers.iteritems():
                # if header in ['content-length', 'content-disposition']:
                if header in ['content-disposition']:
                    resp[header] = value

        return resp
