from django.utils.module_loading import import_by_path
from django.conf import settings

from studiogdo.pip.admin import admin

pathpatterns = import_by_path("pip.admin.%s.pathpatterns" % admin.paths)
