from django.conf.urls import patterns, url
from . import views

urlpatterns = patterns('',
                       url(r"^$", views.blank, name="dj-mongo-reader-root"),
                       url(r"^info/$", views.info),
                       url(r"(?P<db>\w+)/(?P<col>\w+)/$", views.blank, name="dj-mongo-reader-col"),
                       url(r"(?P<db>\w+)/(?P<col>\w+)/(?P<cmd>\w+)$", views.restcall, name="dj-mongo-reader-cmd"),
                       )
