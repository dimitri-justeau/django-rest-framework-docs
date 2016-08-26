from importlib import import_module
from django.conf import settings
from django.core.urlresolvers import RegexURLResolver, RegexURLPattern
from django.utils.module_loading import import_string
from rest_framework.views import APIView
from rest_framework_docs.api_endpoint import ApiNode, ApiEndpoint


class ApiDocumentation(object):

    def __init__(self):
        self.endpoints = []

        try:
            root_urlconf = import_string(settings.ROOT_URLCONF)
        except ImportError:
            # Handle a case when there's no dot in ROOT_URLCONF
            root_urlconf = import_module(settings.ROOT_URLCONF)
        if hasattr(root_urlconf, 'urls'):
            self.get_all_view_names(root_urlconf.urls.urlpatterns)
        else:
            self.get_all_view_names(root_urlconf.urlpatterns)

    def get_all_view_names(self, urlpatterns, parent_api_node=None):
        for pattern in urlpatterns:
            if isinstance(pattern, RegexURLResolver):
                if pattern._regex == "^":
                    parent = parent_api_node
                else:
                    parent = ApiNode(pattern, parent_node=parent_api_node)
                self.get_all_view_names(urlpatterns=pattern.url_patterns, parent_api_node=parent)
            elif isinstance(pattern, RegexURLPattern) and _is_drf_view(pattern) and not _is_format_endpoint(pattern):
                api_endpoint = ApiEndpoint(pattern, parent_api_node)
                self.endpoints.append(api_endpoint)

    def get_endpoints(self):
        return self.endpoints


def _is_drf_view(pattern):
    """
    Should check whether a pattern inherits from DRF's APIView
    """
    return hasattr(pattern.callback, 'cls') and issubclass(pattern.callback.cls,
                                                           APIView)


def _is_format_endpoint(pattern):
    """
    Exclude endpoints with a "format" parameter
    """
    return '?P<format>' in pattern._regex
