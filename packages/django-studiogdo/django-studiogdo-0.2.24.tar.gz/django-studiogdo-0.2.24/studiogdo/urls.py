from django.conf.urls import url, patterns
from studiogdo.views import SkelView

""" deprecated
urlpatterns = patterns('',
    url(r'^$', view=SkelView.as_view(), name='studiogdo'),
    url(r'^(?P<entry>\w+).gdo$', view=SkelView.as_view(), name='studiogdo'),
    url(r'^lock/(?P<entry>\w+).gdo$', view=SkelView.as_view(), name='lock'),
    url(r'^unlock/(?P<entry>\w+).gdo$', view=SkelView.as_view(), name='unlock'),
)
""" 
