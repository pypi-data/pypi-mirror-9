""" PDF Support
"""
from zope.interface import implementer
from zope.security import checkPermission
from Products.Five.browser import BrowserView
from eea.converter.interfaces import ISupport

@implementer(ISupport)
class Support(BrowserView):
    """ PDF Support
    """
    def can_download(self):
        """ Can download context as ePub
        """
        if not checkPermission('eea.epub.download', self.context):
            return False
        return True
