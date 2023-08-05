################################################################
# pp.client-plone
# (C) 2013,  ZOPYX Limited, D-72074 Tuebingen, Germany
################################################################

from ..compatible import InitializeClass
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class HTMLView(BrowserView):
    """ This view renders a HMTL fragment for the configured content type """

    template = ViewPageTemplateFile('newsitem.pt')

    def __call__(self, *args, **kw):
        return self.template(self.context)

InitializeClass(HTMLView)
