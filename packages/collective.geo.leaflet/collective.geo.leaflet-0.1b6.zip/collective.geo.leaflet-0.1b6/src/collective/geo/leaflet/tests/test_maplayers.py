# -*- coding: utf-8 -*-
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collective.geo.leaflet.interfaces import IMapLayer
from collective.geo.leaflet.maplayers import MapLayer
from collective.geo.leaflet.testing import INTEGRATION
from zope.component import provideSubscriptionAdapter
import unittest2 as unittest


class TestGeomap(unittest.TestCase):
    layer = INTEGRATION

    def setUp(self):
        self.portal = self.layer['portal']

    def test_add_map_layer(self):

        class BeautifulMap(MapLayer):
            name = "beautifulmap"
            title = "Beautiful Map"
            index = ViewPageTemplateFile('../browser/layers/osm.pt')

        provideSubscriptionAdapter(
            BeautifulMap, [int], IMapLayer
        )

        bm = BeautifulMap(self.portal, self.portal.REQUEST)
        self.assertTrue(bm.name, "beautifulmap")
        self.assertTrue('<script type="text/javascript"' in bm.index())
