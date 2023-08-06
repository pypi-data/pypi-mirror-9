from django.conf import settings
from django.shortcuts import render
from django.utils.safestring import mark_safe
from django.views.generic.base import TemplateView

from api import ButterCms


class BlogHome(TemplateView):

    default_template_name = "buttercms_blog.html"

    def get_template_names(self):
        try:
            # Check for an overridden blog template.
            return [settings.BUTTER_CMS_BLOG_TEMPLATE]
        except AttributeError:
            # Use default if BUTTER_CMS_BLOG_TEMPLATE is not defined.
            return [self.default_template_name]

    def get_context_data(self, **kwargs):
        context = super(BlogHome, self).get_context_data(**kwargs)

        butter = ButterCms()
        context['recent_posts'] = butter.get_recent_posts()
        return context


class BlogPost(TemplateView):

    default_template_name = "buttercms_blog_post.html"

    def get_template_names(self):
        try:
            # Check for an overridden blog template.
            return [settings.BUTTER_CMS_BLOG_POST_TEMPLATE]
        except AttributeError:
            # Use default if BUTTER_CMS_BLOG_TEMPLATE is not defined.
            return [self.default_template_name]

    def get_context_data(self, **kwargs):
        context = super(BlogPost, self).get_context_data(**kwargs)

        try:
            # Check for an overridden blog template.
            context['base_template'] =  settings.BUTTER_CMS_BLOG_TEMPLATE
        except AttributeError:
            context['base_template'] =  'buttercms_blog.html'

        butter = ButterCms()
        context['post'] = butter.get_post(kwargs['slug'])
        context['post']['body'] = mark_safe(context['post']['body'])
        return context