# -*- coding: utf-8 -*-
from studiogdo.utilities.request import AddRequestDetails


class CustomMiddleware(object):
    """
        Adds user details to request context during request processing, so that they
        show up in the error emails. Add to settings.MIDDLEWARE_CLASSES and keep it
        outermost(i.e. on top if possible). This allows it to catch exceptions in
        other middlewares as well.
    """

    def process_exception(self, request, exception):
        """
        Process the request to add some variables to it.
        """

        # Add other details about the user to the META CGI variables.
        try:
            if request.user.is_authenticated():
                AddRequestDetails(request)
                # request.META['AUTH_VIEW_ARGS'] = str(view_args)
                # request.META['AUTH_VIEW_CALL'] = str(view_func)
                # request.META['AUTH_VIEW_KWARGS'] = str(view_kwargs)
        except:
            pass