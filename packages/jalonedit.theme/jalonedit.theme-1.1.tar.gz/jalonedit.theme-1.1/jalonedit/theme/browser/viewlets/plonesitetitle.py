from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase

from zope.component import getMultiAdapter

class PloneSiteTitle(ViewletBase):

    def update(self):
        self.computed_value = 'any output'
        
        
    def getPloneSiteTitle(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        portal = portal_state.portal()
        return portal.Title()