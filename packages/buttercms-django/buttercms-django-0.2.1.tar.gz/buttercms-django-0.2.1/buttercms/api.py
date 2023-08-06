from django.conf import settings
from django.http import Http404

import requests


DEFAULT_TOKEN = 'f312b970e2598e6d7caf2331b046b199f27890d6'
API_URL = 'https://buttercms.com/api/'


class ButterCms(object):
    def __init__(self):
        try:
            self.api_key = settings.BUTTER_CMS_TOKEN
        except AttributeError:
            self.api_key = DEFAULT_TOKEN

    def get_auth_header(self):
        return {'Authorization': 'Token %s' % self.api_key}

    def get_recent_posts(self):
        try:
            response = requests.get('%sposts/' % API_URL, headers=self.get_auth_header())
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            raise Http404("Blog does not exist.")
        except:
            raise Http404("An error occured retrieving blog. Please try again later.")

        return response.json()

    def get_post(self, slug):
        try:
            response = requests.get('%sposts/%s' % (API_URL, slug), headers=self.get_auth_header())
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            raise Http404("Blog post does not exist.")
        except:
            raise Http404("An error occured retrieving blog post. Please try again later.")

        return response.json()