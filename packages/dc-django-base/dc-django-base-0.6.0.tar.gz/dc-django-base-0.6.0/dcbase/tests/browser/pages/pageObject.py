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
    def _constructPathUrlPath(cls, urlFields):
        url = reverse(cls._urlPattern, kwargs=urlFields)
        return url

    @classmethod
    def get(cls, browser, baseUrl, **urlFields):
        url = cls._constructPathUrlPath(urlFields)
        browser.get(baseUrl + url)
        return cls(browser, **urlFields)

    def _assertBrowserAtThisPage(self):
        expectedPath = self._constructPathUrlPath(self._urlFields)

        currentUrl = self.browser.current_url
        result = urlparse(currentUrl)
        actualPath = result.path

        if expectedPath != actualPath:
            raise RuntimeError('Current browser page (%s) is not expected %s page (%s)' % (actualPath, self._pageName, expectedPath))

    def hasElementWithId(self, elementId):
        element = self.getElementOrNoneById(elementId)
        return element is not None

    def hasSuccessAlert(self):
        return self._hasAlert('success')

    def hasErrorAlert(self):
        return self._hasAlert('danger')

    def _hasAlert(self, alertType):
        return len(self.browser.find_elements_by_class_name('alert-%s' % alertType)) is not 0

    def getElementOrNoneById(self, id):
        try:
            return self.browser.find_element_by_id(id)
        except:
            return None

    def getElementOrNoneByLinkText(self, text):
        try:
            return self.browser.find_element_by_link_text(text)
        except:
            return None

