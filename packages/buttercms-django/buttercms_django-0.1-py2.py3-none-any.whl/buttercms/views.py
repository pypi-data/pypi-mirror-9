from django.conf import settings
from django.shortcuts import render
from django.utils.safestring import mark_safe

import requests


def blog_home(request):
    context = {}

    headers = {'Authorization': 'Token %s' % settings.BUTTER_CMS_TOKEN}
    response = requests.get('http://127.0.0.1:8000/posts/', headers=headers)
    recent_posts = response.json()

    context['recent_posts'] = recent_posts
    return render(request, 'blog.html', context)


def blog_post(request, slug):
    context = {}

    headers = {'Authorization': 'Token %s' % settings.BUTTER_CMS_TOKEN}
    response = requests.get('http://127.0.0.1:8000/posts/%s' % slug, headers=headers)
    post = response.json()

    context['post'] = post
    context['post']['body'] = mark_safe(context['post']['body'])
    return render(request, 'blog_post.html', context)
