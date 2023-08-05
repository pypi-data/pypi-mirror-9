# -*- coding: utf-8 -*-
from collective.geo.leaflet import geomap

from plone.app.layout.viewlets import common

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from zope.component import getMultiAdapter
import logging
logger = logging.getLogger("collective.geo.leaflet")


class ContentViewlet(common.ViewletBase):

    index = ViewPageTemplateFile('templates/leafletcontentviewlet.pt')

    def __init__(self, context, request, view, manager=None):
        super(ContentViewlet, self).__init__(context, request, view, manager)
        self.geomap = geomap.GeoMap(context, request)

    @property
    def coordinates(self):
        view = getMultiAdapter((self.context, self.request), name="geoview")
        return view.getCoordinates()

    @property
    def map_viewlet_position(self):
        if self.geomap.has_map:
            return self.geomap.geo_feature_style.get('map_viewlet_position')

    def render(self):
        if self.manager.__name__ != self.map_viewlet_position:
            return ''

        type, coords = self.coordinates
        if type and coords:
            return super(ContentViewlet, self).render()
        else:
            return ''

    def make_popup(self):
        # XXX should be in a template
        popup = "<div class='geo-popup'>"
        geo_infos = self.geomap.geo_feature_style
        for prop in geo_infos.get('display_properties', []):
            if hasattr(self.context, prop):
                popup += getattr(self.context, prop)()
                popup += '<br />'
            else:
                logger.info("Type {} has no attribute : {}".format(
                    self.context.portal_type,
                    prop))
        popup += "</div>"
        return popup

    def geojson(self):
        return getMultiAdapter(
            (self.context, self.request),
            name="geo-json.json"
        )
