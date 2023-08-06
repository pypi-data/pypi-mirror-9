from django.conf.urls import patterns, url

from .views import BlogHome, BlogPost

urlpatterns = [
    url(r'^$', BlogHome.as_view(), name='blog'),
    url(r'^(?P<slug>.*)$', BlogPost.as_view(), name='blog_post'),
]