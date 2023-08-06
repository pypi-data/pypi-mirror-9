from incuna_test_utils.testcases.api_request import BaseAPIRequestTestCase
from tests.factories import UserFactory


class APIRequestTestCase(BaseAPIRequestTestCase):
    user_factory = UserFactory

    def test_create_request_format(self):
        request = self.create_request()
        assert request.META['format'] == 'json'

    def test_create_request_auth(self):
        request = self.create_request()
        assert request.user.is_authenticated()

    def test_create_request_no_auth(self):
        request = self.create_request(auth=False)
        assert not request.user.is_authenticated()
