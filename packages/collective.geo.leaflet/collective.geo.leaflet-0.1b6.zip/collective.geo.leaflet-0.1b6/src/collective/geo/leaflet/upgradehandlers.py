# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName


def upgrade_1_to_2(context):
    setup = getToolByName(context, 'portal_setup')
    setup.runAllImportStepsFromProfile('profile-collective.geo.leaflet:default')