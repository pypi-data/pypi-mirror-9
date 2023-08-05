# -*- coding: utf-8 -*-
"""
This module contains IMapLayer implementations for commonly available
base maps. These layers can be configured in the geo-settings control panel
or may be re-used in manually configured map-widgets.
"""
from zope.interface import implements
from zope.component import provideAdapter

from collective.geo.leaflet.interfaces import IMapLayer
from collective.geo.leaflet.interfaces import ICollectiveGeoLeafletLayer

from collective.geo.leaflet import _

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class MapLayer(object):
    '''
    An empty IMapLayer implementation, useful as base class.
    MapLayers are named components specific for
    '''
    implements(IMapLayer)
    # we need a property to evaluate if the layer map is based on google
    # or bing maps to include a external javascrpt
    type = 'baselayer'
    google = False

    def __init__(self, context, request):
        self.request = request
        self.context = context
        self.register_view()

    @property
    def title(self):
        return self.__class__.__name__

    @property
    def name(self):
        return self.title.lower()

    def view_name(self):
        return "{}-leaflet-layer".format(self.name)

    def register_view(self):
        """register a view to call js associated with layer """
        provideAdapter(
            factory=self.__class__,
            adapts=(None, None),
            provides=ICollectiveGeoLeafletLayer,
            name=self.view_name())


class OpenStreetMap(MapLayer):
    name = u"osm"
    title = _(u"Open Street Map")
    index = ViewPageTemplateFile('browser/layers/osm.pt')


class GoogleStreetMapLayer(MapLayer):
    name = u"google_map"
    title = _(u"Google")
    index = ViewPageTemplateFile('browser/layers/google_map.pt')
    google = True


class GoogleSatelliteMapLayer(MapLayer):
    name = u"google_sat"
    title = _(u"Satellite (Google)")
    index = ViewPageTemplateFile('browser/layers/google_sat.pt')
    google = True


class GoogleHybridMapLayer(MapLayer):
    name = u"google_hyb"
    title = _(u"Hybrid (Google)")
    index = ViewPageTemplateFile('browser/layers/google_hyb.pt')
    google = True


class GoogleTerrainMapLayer(MapLayer):
    name = u"google_ter"
    title = _(u"Terrain (Google)")
    index = ViewPageTemplateFile('browser/layers/google_ter.pt')
    google = True
