from urllib.parse import urlparse
from django.core.urlresolvers import reverse


class PageObject(object):
    _urlPattern = 'INVALID'
    _pageName = 'UNKNOWN PAGE NAME'

    def __init__(self, browser, **urlFields):
        self.browser = browser
        self._urlFields = urlFields
        self._assertBrowserAtThisPage()

    @classmethod
    def get_url(cls, urlFields):
        url = reverse(cls._urlPattern, kwargs=urlFields)
        return url

    @classmethod
    def get(cls, browser, baseUrl, **urlFields):
        url = cls.get_url(urlFields)
        browser.get(baseUrl + url)
        return cls(browser, **urlFields)

    def _assertBrowserAtThisPage(self):
        expectedPath = self.get_url(self._urlFields)

        currentUrl = self.browser.current_url
        result = urlparse(currentUrl)
        actualPath = result.path

        if expectedPath != actualPath:
            raise RuntimeError('Current browser page (%s) is not expected %s page (%s)' % (actualPath, self._pageName, expectedPath))

    def hasElementWithId(self, elementId):
        element = self.getElementOrNoneById(elementId)
        return element is not None

    def getElementOrNoneById(self, elementId):
        try:
            return self.browser.find_element_by_id(elementId)
        except:
            return None

    def getElementOrNoneByLinkText(self, text):
        try:
            return self.browser.find_element_by_link_text(text)
        except:
            return None
