=========
StudioGdo
=========

StudioGdo is a MVC extension framework. It allows to use simply ORM Model in HTML Templates using path notation.

This module is just for now the Java/Django interface and will be completed to be self contained once all source will be rewritten in Python.

To get more informations on project (documentation and milestones) please contact:

gdoumenc@studiogdo.com, eklein@123imprim.com

========
Settings
========

STUDIOGDO_FACET =
    "django"  # to use the django template renderer
    "java"    # to use the java template renderer

STUDIOGDO_HOST = "url_to_you_studiogdo_server"

STUDIOGDO_SERVLET = "servlet/prefix"


TEMPLATE_CONTEXT_PROCESSORS = (..., 'studiogdo.context_processors.include_studiogdo_address', ...)

MIDDLEWARE_CLASSES = (..., 'studiogdo.middleware.APICookies', ...)