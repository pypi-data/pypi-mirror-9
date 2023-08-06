"""
Interface for all Plugins
"""

class Plugin(object):

    def match(self, page):
        pass

    def run(self, page):
        pass

    def startup(self, context):
        pass

    def shutdown(self, crawler):
        pass
