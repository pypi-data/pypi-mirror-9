# Django imports
from django.conf.urls import patterns, include, url


from djhcup_integration import views


# base patterns always available through having djhcup_core installed
urlpatterns = patterns('',
    url(r'$', views.Index.as_view(), name='djhcup_integration|index'),
)