from django.conf import settings


def include_studiogdo_address(request):
    return {
        'studiogdo_host': settings.STUDIOGDO_HOST,
        'studiogdo_servlet': settings.STUDIOGDO_SERVLET,
        'studiogdo_debug': settings.STUDIOGDO_DEBUG or False,
    }
