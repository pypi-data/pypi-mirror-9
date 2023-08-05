import json
import requests
import responses
import unittest

from kaizen.client import ApiClient


class ApiClientTest(unittest.TestCase):

    def setUp(self):
        self._client = ApiClient("fake_api_key")

    @responses.activate
    def test_issue_request(self):
        items = {"items": [1, 2]}
        params = {"k": "v"}
        responses.add(responses.GET, "https://agilezen.com/api/v1/fake_url?k=v",
                      match_querystring=True, body=json.dumps(items), status=200,
                      content_type="application/json")
        self.assertEquals(self._client.make_request("GET", "fake_url", params),
                          items)

    @responses.activate
    def test_request_raises(self):
        responses.add(responses.GET, "https://agilezen.com/api/v1/fake_url",
                      status=404, content_type='application/json')
        self.assertRaises(requests.HTTPError, self._client.make_request, "GET",
                          "fake_url")

if __name__ == "__main__":
    unittest.main()
