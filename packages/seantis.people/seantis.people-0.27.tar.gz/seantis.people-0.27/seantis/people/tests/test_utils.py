from uuid import uuid4
from seantis.people import tests, utils

class TestUtils(tests.IntegrationTestCase):

    def test_uuid_list(self):

        # works
        utils.UUIDList((uuid4(), uuid4()))

        # fails
        self.assertRaises(ValueError, lambda: utils.UUIDList(('test', )))
