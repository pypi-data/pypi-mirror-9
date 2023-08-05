"""This module deals with HTTP related concerns regarding AgileZen API."""
import json
import logging
import requests

_LOG = logging.getLogger(__name__)
# requests logs a line every time a new connection is established
logging.getLogger("requests").setLevel(logging.ERROR)


class ApiClient(object):
    """Ease making calls to AgileZen API."""

    def __init__(self, api_key):
        """
        Args:
            api_key: the AgileZen api key
        """
        self._api_key = api_key

    def make_request(self, verb, url, params=None, data=None, headers=None):
        """Send a HTTP request to the given url along with params, data and
        headers.

        Args:
            verb: HTTP verb to use
            url: path to the resource to send the request to
            params: url parameters to send
            data: paylaod to send
            headers: headers to send
        Returns:
            the dict loaded from the json response
        Raises:
            a requests.HTTPError if the status code is not OK
        """
        default_dict = lambda x: x if x else {}
        url = self._get_url(url)
        headers = default_dict(headers)
        data = json.dumps(default_dict(data))
        response = requests.request(verb, url, params=default_dict(params),
                                    data=data,
                                    headers=self._get_headers(headers))
        response.raise_for_status()
        _LOG.debug("request issued to '%s' [%s s]", url,
                   response.elapsed.total_seconds())
        return response.json()

    def _get_url(self, resource_path):
        """Return the full URL to an API resource

        Args:
            resource_path: path to the resource from the API root
        """
        return "https://agilezen.com/api/v1/%s" % resource_path

    def _get_headers(self, headers):
        """Return the given headers update with headers required by the API.

        Args:
            headers: headers provided by the user
        """
        headers.update({
            "Accept": "application/json",
            "Content-type": "application/json",
            "X-Zen-ApiKey": self._api_key
        })
        return headers

