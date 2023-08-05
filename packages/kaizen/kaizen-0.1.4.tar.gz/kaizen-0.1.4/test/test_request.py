import unittest

from kaizen.request import VERBS, Request


class VerbsTest(unittest.TestCase):

    def testIn(self):
        self.assertIn("GET", VERBS)
        self.assertIn("POST", VERBS)
        self.assertIn("PUT", VERBS)
        self.assertIn("DELETE", VERBS)

    def testNotIn(self):
        self.assertNotIn("NoWay", VERBS)
        self.assertNotIn("OPTIONS", VERBS)
        self.assertNotIn("HEAD", VERBS)


class RequestTest(unittest.TestCase):

    def setUp(self):
        self._request = Request()

    def testSetVerb(self):
        def assign_verb(new_verb):
            """To make it possible to use assertRaises."""
            self._request.verb = new_verb
        self.assertRaises(ValueError, assign_verb, "Nop!")
        self.assertRaises(ValueError, self._request.update_verb, "Nop!")

    def testCallChaining(self):
        post_request = self._request.update_verb("POST").update_url("/call_me")\
            .update_params({"name": "popo"}).update_data({"text": "cool beans"})
        self.assertEquals(post_request, self._request)
        self.assertEquals(post_request.verb, "POST")
        self.assertEquals(post_request.url, "/call_me")
        self.assertDictEqual(post_request.params, {"name": "popo"})
        self.assertDictEqual(post_request.data, {"text": "cool beans"})

