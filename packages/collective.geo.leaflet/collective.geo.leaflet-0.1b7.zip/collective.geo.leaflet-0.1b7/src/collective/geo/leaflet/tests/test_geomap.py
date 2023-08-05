# -*- coding: utf-8 -*-
import unittest2 as unittest
from collective.geo.geographer.interfaces import IGeoreferenceable
from collective.geo.geographer.interfaces import IWriteGeoreferenced
from collective.geo.leaflet.testing import INTEGRATION
from collective.geo.leaflet.geomap import GeoMap
from collective.geo.settings.interfaces import IGeoFeatureStyle
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from zope.interface import alsoProvides
import json
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


class TestGeomap(unittest.TestCase):
    layer = INTEGRATION

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory("Document", "doc")
        self.doc = self.portal.doc
        alsoProvides(self.doc, IGeoreferenceable)
        self.geo = IWriteGeoreferenced(self.doc)
        self.geo.setGeoInterface('Point', (5.583, 50.633))
        self.doc.reindexObject(idxs=['zgeo_geometry', 'collective_geo_styles'])

    def test_init_geomap(self):
        geomap = GeoMap(self.portal, self.portal.REQUEST)
        self.assertFalse(geomap.has_map)

        geomap = GeoMap(self.doc, self.doc.REQUEST)
        self.assertTrue(geomap.has_map)

    def test_geo_feature_style(self):
        geomap = GeoMap(self.doc, self.doc.REQUEST)

        geo_feature_style = geomap.geo_feature_style
        self.assertEqual(
            geo_feature_style['marker_image'],
            "http://nohost/plone/++resource++collective.js.leaflet/images/marker-icon.png",
            'Incorect default marker image url')

        registry = getUtility(IRegistry)
        registry['collective.geo.settings.interfaces.IGeoFeatureStyle.linewidth'] = float(3.0)

        manager = IGeoFeatureStyle(self.doc, None)
        manager.set('use_custom_styles', False)
        manager.set('linewidth', float(11.0))
        self.doc.reindexObject(idxs=['zgeo_geometry', 'collective_geo_styles'])

        geomap = GeoMap(self.doc, self.doc.REQUEST)
        geo_feature_style = geomap.geo_feature_style

        self.assertEqual(geo_feature_style["linewidth"], 3.0)

        manager.set('use_custom_styles', True)
        self.doc.reindexObject(idxs=['zgeo_geometry', 'collective_geo_styles'])

        geomap = GeoMap(self.doc, self.doc.REQUEST)
        geo_feature_style = geomap.geo_feature_style

        self.assertEqual(geo_feature_style["linewidth"], 11.0)

    def test_geo_settings(self):
        geomap = GeoMap(self.doc, self.doc.REQUEST)
        geo_settings = geomap.geo_settings
        self.assertIn(u'osm', geo_settings['default_layers'])

    def test_default_layers(self):
        geomap = GeoMap(self.doc, self.doc.REQUEST)
        baselayers = json.loads(geomap.default_layers()['baselayers'])
        keys = [key['name'] for key in baselayers]
        self.assertIn('osm', keys)

    def test_inline_style(self):
        geomap = GeoMap(self.doc, self.doc.REQUEST)
        self.assertEqual(geomap.inline_style(), 'width: 100%;height: 600px')

    def test_coordinates(self):
        geomap = GeoMap(self.doc, self.doc.REQUEST)
        self.assertEqual(geomap.coordinates['latitude'], 50.633)
