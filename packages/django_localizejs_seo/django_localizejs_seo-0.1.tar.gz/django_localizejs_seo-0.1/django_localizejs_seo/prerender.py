import settings

import re
import requests

from django.http import HttpResponse

import logging
logger = logging.getLogger(__name__)


class LocalizeSEOMiddleware(object):

    def __init__(self, *args, **kwargs):
        regex_str = "|".join(settings.USER_AGENTS)
        regex_str = ".*?(%s)" % regex_str
        self.USER_AGENT_REGEX = re.compile(regex_str, re.IGNORECASE)
        self.BASE_URL = settings.PRERENDER_URL
        self.session = requests.Session()

    def process_request(self, request):
        # import ipdb; ipdb.set_trace()
        if not settings.ENABLED:
            return

        # TBI makesure rootDomain is available
        if self.ignore_request(request):
            return

        if "HTTP_USER_AGENT" not in request.META:
            return

        if not self.USER_AGENT_REGEX.match(request.META["HTTP_USER_AGENT"]):
            return

        render_url = self.build_render_url(request)  # TBI

        try:
            return self.get_response(render_url)  # TBI
        except Exception as e:
            logger.Exception(e)

    def ignore_request(self, request):
        for url in settings.IGNORE_URLS:
            if url in request.path:
                return True

        extension = None
        last_dot = request.path.rfind(".")
        if last_dot == -1:
            return False

        extension = request.path[last_dot:]
        return extension and extension in settings.IGNORE_EXTENSIONS

    def build_render_url(self, request):
        url = '{scheme}://{host}{path}'.format(
            scheme=request.scheme,
            host=request.get_host(),
            path=request.path,
        )

        if "//" not in url:
            raise ValueError("Invalid url: %s" % url)
        render_url = "%s?url=%s" % (self.BASE_URL, url)
        return render_url

    def get_response(self, url):
        response = self.session.get(url)
        assert response.status_code < 500
        r = HttpResponse(response)
        r.status_code = response.status_code
        return r
