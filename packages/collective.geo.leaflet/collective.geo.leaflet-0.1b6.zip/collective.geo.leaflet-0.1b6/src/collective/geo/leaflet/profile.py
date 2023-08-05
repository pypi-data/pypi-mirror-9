# -*- coding: utf-8 -*-
from zope.interface import implements

from Products.CMFPlone.interfaces import INonInstallable
from Products.CMFQuickInstallerTool.interfaces import INonInstallable as INonQ

DEPENDENCIES = [
    u'collective.geo.geographer',
    u'collective.geo.settings',
    u'collective.geo.behaviour',
    u'collective.geo.openlayers',
    u'collective.geo.mapwidget',
    u'collective.z3cform.mapwidget',
    u'collective.z3cform.colorpicker',
    u'collective.geo.contentlocations',
    u'collective.geo.json',
    u'collective.js.leaflet',
]


class HiddenProfiles(object):
    implements(INonInstallable)

    def getNonInstallableProfiles(self):
        _dependencies = ['%s:default' % item for item in DEPENDENCIES]
        return _dependencies + ['collective.js.leaflet:uninstall']


class HiddenProducts(object):
    implements(INonQ)

    def getNonInstallableProducts(self):
        return DEPENDENCIES
