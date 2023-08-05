# -*- coding: utf-8 -*-
from zope.publisher.browser import BrowserView

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class CollectiveGeoLeafletMacros(BrowserView):
    template = ViewPageTemplateFile('templates/collectivegeoleaflet_macros.pt')

    def __getitem__(self, key):
        return self.template.macros[key]
