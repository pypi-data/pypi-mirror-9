

class Page(object):

    def __init__(self, crawler, browser):
        self.crawler = crawler
        self.browser = browser
        self.initial = ''
        self.url = ''

    @property
    def path(self):
        return ''

    def links(self):
        links = self.browser.driver.execute_script("return Qe.links()")
        return set(links)
