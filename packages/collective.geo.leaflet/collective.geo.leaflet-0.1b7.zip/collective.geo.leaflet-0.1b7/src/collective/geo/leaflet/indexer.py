# -*- coding: utf-8 -*-
from plone.indexer.decorator import indexer
from collective.geo.mapwidget.utils import get_feature_styles
from plone.dexterity.interfaces import IDexterityContent


@indexer(IDexterityContent)
def collective_geo_styles(context):
    styles = get_feature_styles(context)
    return styles
