from django.core.urlresolvers import reverse


class RequiresLogin(object):
    def test_getRedirectsToLoginIfUserNotLoggedIn(self):
        self.logOut()
        url = self.get_url()
        response = self.client.get(url)
        self.assertRedirects(response, reverse('account_login') + '?next={}'.format(url))

    def test_getReturnsStatusOkForLoggedInUsers(self):
        if not self.loggedInUser:
            user = self.createUser()
            self.logInAs(user)
        self.get()
        self.assertResponseStatusIsOk(self.response)

