# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

from collective.geo.leaflet import geomap
from zope.component import getMultiAdapter
import json


class GeoLeaflet(BrowserView):

    index = ViewPageTemplateFile("templates/geo-leaflet.pt")

    def __init__(self, context, request):
        super(GeoLeaflet, self).__init__(context, request)
        self.geomap = geomap.GeoMap(context, request)

    def __call__(self):
        return self.render()

    def render(self):
        return self.index()

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    def geojson_urls(self):
        query_dict = {}
        query_dict['path'] = {'query': '/'.join(self.context.getPhysicalPath()), 'depth': 1 }
        query_dict['portal_type'] = 'Collection'
        brains = self.portal_catalog(query_dict)
        if len(brains) > 1:
            urls = []
            for brain in brains:
                urls.append("{}/@@geo-json.json".format(brain.getURL()))
        else:
            urls = ["{}/@@geo-json.json".format(self.context.absolute_url())]
        return json.dumps(urls)

    def geojson(self):
        return getMultiAdapter(
            (self.context, self.request),
            name="geo-json.json"
        )
