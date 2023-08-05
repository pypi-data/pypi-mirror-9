# -*- coding: utf-8 -*-
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.schema import TextLine


class ICollectiveGeoLeafletLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class ILeafletViewlet(Interface):
    """Marker interface for Viewlet """


class IMapLayer(Interface):
    """Marker interface for geo layers independent of geo js library"""

    name = TextLine(title=u'Id')
    title = TextLine(title=u'Title')

    def jsfactory():
        pass
