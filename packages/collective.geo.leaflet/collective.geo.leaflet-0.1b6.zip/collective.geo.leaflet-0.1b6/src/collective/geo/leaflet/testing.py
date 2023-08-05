# -*- coding: utf-8 -*-
from plone.app.testing import PloneWithPackageLayer
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
import collective.geo.leaflet
from plone.app.robotframework.testing import AUTOLOGIN_LIBRARY_FIXTURE

from plone.testing import z2


FIXTURE = PloneWithPackageLayer(zcml_filename="testing.zcml",
                                zcml_package=collective.geo.leaflet,
                                additional_z2_products=[],
                                gs_profile_id='collective.geo.leaflet:testing',
                                name="collective.geo.leaflet:FIXTURE")

INTEGRATION = IntegrationTesting(bases=(FIXTURE,),
                                 name="collective.geo.leaflet:Integration")

FUNCTIONAL = FunctionalTesting(bases=(FIXTURE,),
                               name="collective.geo.leaflet:Functional")

ROBOT = FunctionalTesting(bases=(FIXTURE,
                                 AUTOLOGIN_LIBRARY_FIXTURE,
                                 z2.ZSERVER_FIXTURE),
                          name="ROBOT")
