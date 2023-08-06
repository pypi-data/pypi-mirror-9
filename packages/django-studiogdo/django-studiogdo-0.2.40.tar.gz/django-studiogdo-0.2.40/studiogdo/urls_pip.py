from django.conf.urls import url, patterns
from django.conf import settings
from studiogdo.views import cached_javascript_catalog
from studiogdo.pip.views import LoginView, AccueilView

login_url = getattr(settings, 'LOGIN_URL')
if login_url.startswith("/"):
    login_url = login_url[1:]
urlpatterns = patterns('',
                       url(r'^%s$' % login_url, view=LoginView.as_view(), name="login"),
                       url(r'^$', view=AccueilView.as_view(), name="accueil"),
                       )


urlpatterns += patterns('',
                        url(r'^jsi18n/$', cached_javascript_catalog, name="javascript_catalog"),
                        )
