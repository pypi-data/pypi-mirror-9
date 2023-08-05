import unittest

from kaizen.api import ZenRequest, ChainingError

class ZenRequestTest(unittest.TestCase):

    def testChainingProjectPhase(self):
        request = ZenRequest("fake_key")
        self.assertRaises(ChainingError, request.phases)


if __name__ == "__main__":
    unittest.main()
