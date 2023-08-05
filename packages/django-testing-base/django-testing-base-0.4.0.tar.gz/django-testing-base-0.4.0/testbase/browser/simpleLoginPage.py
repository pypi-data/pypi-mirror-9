from django.conf import settings
from testbase.browser import PageObject


class SimpleLoginPage(PageObject):
    USERNAME_FIELD_ID = 'id_username'
    PASSWORD_FIELD_ID = 'id_password'
    SUBMIT_BUTTON_ID = 'id_submit'

    @classmethod
    def get_url(cls, urlFields):
        return settings.LOGIN_URL

    def enter_username(self, username):
        input = self.browser.find_element_by_id(self.USERNAME_FIELD_ID)
        input.clear()
        input.send_keys(username)

    def enter_password(self, password):
        input = self.browser.find_element_by_id(self.PASSWORD_FIELD_ID)
        input.clear()
        input.send_keys(password)

    def submit_login(self):
        button = self.browser.find_element_by_id(self.SUBMIT_BUTTON_ID)
        button.click()

