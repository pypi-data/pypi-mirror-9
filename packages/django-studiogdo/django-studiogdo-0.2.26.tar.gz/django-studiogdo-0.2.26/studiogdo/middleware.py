import datetime
from django.contrib.auth import logout
from studiogdo.api import StudiogdoApi
from studiogdo.skel.renderer import HTMLRenderer


class APICookies(object):

    def process_request(self, request):
        """ Store tomcat cookie to preserve session """

        # create the Studiogdo API and HTML renderer
        api = StudiogdoApi(cookies=request.COOKIES)
        request.studiogdo_api = api
        request.html_renderer = HTMLRenderer(api)

        return None

    def process_response(self, request, response):
        """ Reset tomcat cookie to preserve session """

        # add studiogdo cookies (if process_request was done)
        if hasattr(request, "studiogdo_api"):
            for cookie in request.studiogdo_api.studiogdo_cookies:
                response.set_cookie(key=cookie.name, value=cookie.value,
                                    expires=cookie.expires, path=cookie.path,
                                    domain=cookie.domain, secure=cookie.secure)

        return response


class Timeout(object):

    def process_request(self, request):
        return None
        if request.user.is_authenticated():
            if 'lastRequest' in request.session:
                elapsedTime = datetime.datetime.now() - request.session['lastRequest']
                if elapsedTime.seconds > 15*60:
                    del request.session['lastRequest']
                    logout(request)

            request.session['lastRequest'] = datetime.datetime.now()
        else:
            if 'lastRequest' in request.session:
                del request.session['lastRequest']

        return None
