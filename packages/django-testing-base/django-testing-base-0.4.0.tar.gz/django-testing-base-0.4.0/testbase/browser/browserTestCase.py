import os
from django.contrib.auth import SESSION_KEY
from django.contrib.sessions.models import Session
from selenium import webdriver
from django.test import LiveServerTestCase
from testbase import BaseTestCase


class BrowserTestCase(LiveServerTestCase, BaseTestCase):
    _pageClass = None
    _browser = None
    _windowWidth = 1024
    _windowHeight = 768
    _loginPage = None

    def __init__(self, methodName):
        super().__init__(methodName)
        self._urlFields = {}

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        webDriverClassName = os.environ.get('BROWSER', 'Chrome')
        webDriverClass = getattr(webdriver, webDriverClassName)
        cls._browser = webDriverClass()
        cls._browser.set_window_size(cls._windowWidth, cls._windowHeight)
        cls._savedObjects = set()
        cls._loggedInUser = None

    @classmethod
    def tearDownClass(cls):
        cls._browser.quit()
        super().tearDownClass()

    def setUp(self):
        BaseTestCase.setUp(self)
        super().setUp()
        self._restoreSavedObjects()
        if self._loginPage is not None and not type(self)._loggedInUser:
            user = self.createUser()
            self.logInAs(user)
            self._saveUserAndSession(user)
        self.browseToPageUnderTest()

    @property
    def pageClass(self):
        return self._pageClass

    @property
    def browser(self):
        return self._browser

    def browseToPage(self, cls, **urlFields):
        self.page = cls.get(self._browser, self.live_server_url, **urlFields)

    def browseToPageUnderTest(self):
        self.browseToPage(self._pageClass, **self._urlFields)

    def logInAs(self, user=None, *, password=None):
        if self._loginPage is None:
            raise RuntimeError('No Log In page provided; set the _loginPage class attribute')
        if user is None:
            user = self.createUser()
        self.browseToPage(self._loginPage)
        self.page.enter_username(user.username)
        self.page.enter_password(self.getPasswordForUser(user))
        self.page.submit_login()
        type(self)._loggedInUser = user
        return user

    def logOut(self):
        raise RuntimeError('No Log Out method provided for tests. Subclass BrowserTestCase and override logOut')

    def _saveUserAndSession(self, user):
        type(self)._savedObjects.add(user)
        session = self._findSessionForUser(user)
        if session is not None:
            type(self)._savedObjects.add(session)

    def _findSessionForUser(self, user):
        sessions = Session.objects.all()
        for session in sessions:
            data = session.get_decoded()
            userId = data.get(SESSION_KEY)
            if userId == user.pk:
                return session
        return None

    def _restoreSavedObjects(self):
        for obj in type(self)._savedObjects:
            obj.save()

