import requests

from django.conf import settings
from django.utils.http import urlquote


class BaseBackend(object):
    host = None
    method = 'POST'

    def send(self, data, params=None, headers=None):
        if self.host is None:
            return

        response = requests.request(self.method, self.host,
                                    data=data, headers=headers,
                                    params=params)
        return response

    def get_user_id(self, request):
        user = getattr(request, 'user', None)
        if user and user.is_authenticated():
            return user.pk
        else:
            return self.get_anonymous_id(request)

    def get_client_ip(self, request):
        try:
            return request.META['HTTP_X_FORWARDED_FOR'].split(',')[0].strip()
        except KeyError:
            return request.META.get('REMOTE_ADDR', '0.0.0.0')

    def get_anonymous_id(self, request):
        host = self.get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', host)
        user_id = hash(''.join([host, user_agent]))
        return 'anon-%s' % user_id

    def page(self, request, host, path):
        # Override this method to send page views
        pass


class GoogleAnalytics(BaseBackend):
    host = 'https://ssl.google-analytics.com/collect'

    def __init__(self):
        self.analytics_key = getattr(settings, 'GOOGLE_ANALYTICS_KEY', None)

    def page(self, request, response):
        host = request.META.get('HTTP_HOST')
        source_ip = self.get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT')
        user_agent_quoted = urlquote(user_agent)
        path = request.get_full_path()
        cid = self.get_user_id(request)

        # UA does not support X-Forwarded-For yet.
        #ip = request.META.get('REMOTE_ADDR')

        headers = {
            'User-Agent': user_agent,
        }
        data = {
            'v': 1,                         # Version
            'tid': self.analytics_key,      # UA-xxxxx
            'cid': cid,                     # Anonymous Client ID
            't': 'pageview',                # Hit type
            'dh': host,                     # Document hostname
            'dp': path,                     # Page
            'uip': source_ip,               # Override IP
            'ua': user_agent_quoted         # Override User-Agent
        }

        self.send(data, headers=headers)
