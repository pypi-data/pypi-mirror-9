import string

from abc import ABCMeta, abstractmethod
from random import choice
from django.contrib.auth.models import User
from django.utils import translation


class BaseTestCase(metaclass=ABCMeta):
    def setUp(self):
        self._loggedInUser = None
        self._passwordsByUser = {}

    def tearDown(self):
        translation.activate('en')

    @abstractmethod
    def logInAs(self, user, *, password=None):
        pass

    @abstractmethod
    def logOut(self):
        pass

    @property
    def loggedInUser(self):
        return self._loggedInUser

    def randStr(self, length=10):
        return ''.join(choice(string.ascii_letters + string.digits) for x in range(length))

    def createUser(self, userName=None, password=None, *, email=None):
        userName = userName or self.randStr()
        password = password or self.randStr()
        email = email or '%s@host.com' % self.randStr()

        user = User.objects.create_user(username=userName, password=password, email=email, first_name=self.randStr(), last_name=self.randStr())
        self._cachePasswordForUser(user, password)

        return user

    def createAdminUser(self, userName=None, password=None, *, email=None, save=True):
        user = self.createUser(userName, password, email=email)
        user.is_staff = True
        if save:
            user.save()
        return user

    def createSuperUser(self, userName=None, password=None, email=None):
        user = self.createAdminUser(userName, password, email=email, save=False)
        user.is_superuser = True
        user.save()
        return user

    def expireSession(self, session):
        session.set_expiry(-1)
        session.save()

    def getPasswordForUser(self, user, default=None):
        return self._passwordsByUser.get(user, default)

    def _cachePasswordForUser(self, user, password):
        self._passwordsByUser[user] = password

