# -*- coding: utf-8 -*-


def AddRequestDetails(request):
    """
        Adds details about the user to the request, so any traceback will include the
        details. Good for troubleshooting; this will be included in the email sent to admins
        on error.
    """
    if request.user.is_anonymous():
        request.META['AUTH_NAME'] = "Anonymous User"
        request.META['AUTH_USER'] = "Anonymous User"
        request.META['AUTH_USER_EMAIL'] = ""
        request.META['AUTH_USER_ID'] = 0
        request.META['AUTH_USER_IS_ACTIVE'] = False
        request.META['AUTH_USER_IS_SUPERUSER'] = False
        request.META['AUTH_USER_IS_STAFF'] = False
        request.META['AUTH_USER_LAST_LOGIN'] = ""
    else:
        request.META['AUTH_NAME'] = str(request.user.first_name) + " " + str(request.user.last_name)
        request.META['AUTH_USER'] = str(request.user.username)
        request.META['AUTH_USER_EMAIL'] = str(request.user.email)
        request.META['AUTH_USER_ID'] = str(request.user.id)
        request.META['AUTH_USER_IS_ACTIVE'] = str(request.user.is_active)
        request.META['AUTH_USER_IS_SUPERUSER'] = str(request.user.is_superuser)
        request.META['AUTH_USER_IS_STAFF'] = str(request.user.is_staff)
        request.META['AUTH_USER_LAST_LOGIN'] = str(request.user.last_login)