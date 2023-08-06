# -*- coding: utf-8 -*-
import re
from base64 import b64decode, b64encode

from django.contrib.auth.decorators import login_required
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect
from django.shortcuts import redirect, render_to_response
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout

from studiogdo.pip import pathpatterns


class PIPView(TemplateView):
    """
    This view checks user is connected to be rendered.
    All templates are in pip folder.
    """

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        # check connected
        api = request.studiogdo_api
        response = api.post_facet(None, '<span data-path="/Session/User(1)"></span>', "dom5")
        facet = unicode(response.content, 'utf-8')
        if not facet:
            data = {}
            data["param1"] = request.user.username
            api.apply_command("/", "Connect", data)

        return super(PIPView, self).dispatch(request, *args, **kwargs)

    def get_template_names(self):
        return 'pip/' + self.template_name


class LoginView(TemplateView):
    template_name = 'pip/login.html'

    def post(self, request, *args, **kwargs):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                auth_login(request, user)
                api = request.studiogdo_api
                data = {}
                data["param1"] = username
                api.apply_command("/", "Connect", data)
                redirect_to = request.GET.get('next', reverse('accueil'))
                return redirect(redirect_to)
            else:
                msg = "Vous avez été déconnecté..."
        else:
            msg = "Paramètres de connexion invalides!"
        c = {}
        c["error_msg"] = msg
        c.update(csrf(request))
        return render_to_response(LoginView.template_name, c)

    def get(self, request, *args, **kwargs):
        """ Disconnect from server. """
        auth_logout(request)
        api = request.studiogdo_api
        api.disconnect()
        return super(LoginView, self).get(request, *args, **kwargs)


class AccueilView(PIPView):
    template_name = 'accueil.html'


class LockView(PIPView):
    pass


class UnlockView(PIPView):
    pass


class PIPPathView(PIPView):
    """
    Adds skel and context from pathes.py in kwargs.
    """
    default_template_name = None

    def dispatch(self, request, *args, **kwargs):
        self.encoded_path = kwargs["path"]
        self.path = b64decode(self.encoded_path)
        path_dict = pathpatterns[self.path]
        context = path_dict.get("context", {})
        kwargs.update(context)
        self.template_name = path_dict.get("template_name", self.default_template_name)
        self.path_group = path_dict.get("path_group", {})
        self.skel = path_dict["skel"]
        kwargs["skel"] = self.skel
        return super(PIPPathView, self).dispatch(request, *args, **kwargs)


class PIPListView(PIPPathView):
    """
    Adds container path (data-path) and iterator slot path (slot) in context.
    """
    default_template_name = "studiogdo/pip/list.html"

    def get_context_data(self, **kwargs):
        # add path
        context = super(PIPListView, self).get_context_data(**kwargs)
        data_path, slot = self.path.rsplit("/", 1)
        # context["data_path"] = self.path
        context["data_path"] = data_path
        context["slot"] = slot
        return context


class PIPDetailsView(PIPPathView):
    """
    Adds stencil path (data-path) and return list path (return-path) in context.
    """
    default_template_name = "studiogdo/pip/details.html"

    def _get_return_path(self):
        slot_path = re.search("(?P<path>.*)\(\d+\)$", self.path)
        if slot_path:
            return slot_path.group("path")
        return ""

    def get_context_data(self, **kwargs):
        context = super(PIPDetailsView, self).get_context_data(**kwargs)
        context["data_path"] = self.path
        context["return_path"] = self._get_return_path()
        return context

    def post(self, request, *args, **kwargs):
        params = request.POST
        api = request.studiogdo_api
        api.post_empty(self.encoded_path, params)
        save_button = params.get("save", None)
        if save_button == "details":
            return HttpResponseRedirect(reverse("details", args=[self.encoded_path]))
        else:
            return HttpResponseRedirect(reverse("list", args=[b64encode(self._get_return_path())]))
