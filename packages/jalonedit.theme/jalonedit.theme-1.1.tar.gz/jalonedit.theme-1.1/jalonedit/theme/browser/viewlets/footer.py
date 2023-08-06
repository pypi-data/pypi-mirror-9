# -*- coding:utf-8 -*-

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from DateTime import DateTime

from zope.component import getMultiAdapter

class Footer(ViewletBase):

    def update(self):
        self.computed_value = 'any output'
  
    def getFooterLinks(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        portal = portal_state.portal()
        abs_url = portal.absolute_url()
        img_url = "%s/++resource++jalonedit.theme.images/navigation/icones/" % abs_url

        return [{"id"    : "home"
                ,"href"  : "%s/cours/presentation" % abs_url
                ,"title" : "Presentation"
                ,"img"   : "%saccueil.png" % img_url
                },
                {"id"    : "map"
                ,"href"  : "%s/cours" %  abs_url
                ,"title" : "Cours"
                ,"img"   : "%splandusite.png" % img_url
                },
                {"id"    : "fichiers"
                ,"href"  : "%s/cours/fichiers" % abs_url
                ,"title" : "Fichiers"
                ,"img"   : "%sressources.png "% img_url
                },
                {"id"    : "help"
                ,"href"  : "%s/cours/aide" % abs_url
                ,"title" : "Aide"
                ,"img"   : "%saide.png" % img_url
                },
                {"id"    : "credits"
                ,"href"  : "%s/cours/credits" % abs_url
                ,"title" : "Credits"
                ,"img"   : "%scredits.png" % img_url
                },
                {"id"    : "accessibility"
                ,"href"  : "%s/accessibility-info" % abs_url
                ,"title" : "Accessibilité"
                ,"img"   : "%saccessibility.png" % img_url
                },
                {"id"    : "print"
                ,"href"  : "javascript:print();"
                ,"title" : "Imprimer la page"
                ,"img"   : "%simprimer.png" % img_url
                }]
        
    def getFooterCredits(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        portal = portal_state.portal()
        abs_url = portal.absolute_url()
        return {"href":"%s/cours/mentions" % abs_url, "title":"Mentions légales", "year":str(DateTime().year()), "unt":"UNS"}