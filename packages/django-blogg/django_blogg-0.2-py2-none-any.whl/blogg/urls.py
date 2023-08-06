from django.conf.urls import patterns, url
from blogg import views, feed


urlpatterns = patterns(
    '',

    url(r'^rss/$', feed.LatestPosts(), name="feed"),

    url(r'^tag/(?P<slug>[\w\-]+)/$', views.tag),

    url(r'^$', views.index),
    url(r'^(?P<slug>[\w\-]+)/$', views.post),
)
