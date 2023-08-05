from django.core.urlresolvers import reverse
from django.http import response as response_mod
from django.test import TestCase
from testbase import BaseTestCase


class UnitTestCase(TestCase, BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)
        super().setUp()
        self._response = None

    def tearDown(self):
        BaseTestCase.tearDown(self)
        super().tearDown()

    def get_url(self):
        raise RuntimeError('No URL provided; supply a url pattern or implement get_url()')

    @property
    def response(self):
        return self._response

    def logInAs(self, user, *, password=None):
        username = user.username
        password = self.getPasswordForUser(user, password)

        result = self.client.login(username=username, password=password)
        if not result:
            raise RuntimeError('Failed to login as user [{}] with password [{}]'.format(username, password))
        self._loggedInUser = user

    def logOut(self):
        self.client.logout()

    def get(self, urlPattern=None, *args, **kwargs):
        if urlPattern is None:
            url = self.get_url()
        else:
            url = reverse(urlPattern, args=args, kwargs=kwargs)
        self._response = self.client.get(url)
        return self._response

    def expireSession(self, session=None):
        if session is None:
            session = self.client.session
        super().expireSession(session)

    def _assertResponseStatusIs(self, response=None, expected_code=response_mod.HttpResponseBase.status_code):
        if response is None:
            response = self.response
        self.assertEqual(expected_code, response.status_code)

    def assertResponseStatusIsOk(self, response=None):
        self._assertResponseStatusIs(response, response_mod.HttpResponseBase.status_code)

    def assertResponseStatusIsNotFound(self, response=None):
        self._assertResponseStatusIs(response, response_mod.HttpResponseNotFound.status_code)

    def assertContextValueEqual(self, response, contextVariableName, expectedValue):
        if contextVariableName not in response.context:
            raise AssertionError('Variable {} not found in context'.format(contextVariableName))
        self.assertEqual(expectedValue, response.context[contextVariableName])

    def assertLastContextValueEqual(self, contextVariableName, expectedValue):
        return self.assertContextValueEqual(self.response, contextVariableName, expectedValue)
