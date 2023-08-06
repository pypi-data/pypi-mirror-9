from django.conf.urls import patterns, url

from .views import blog_home, blog_post

urlpatterns = [
    url(r'^$', blog_home, name='blog'),
    url(r'^(?P<slug>.*)$', blog_post, name='blog_post'),
]