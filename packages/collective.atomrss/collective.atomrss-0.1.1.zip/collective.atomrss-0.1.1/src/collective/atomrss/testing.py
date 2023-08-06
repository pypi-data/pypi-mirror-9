# -*- coding: utf-8 -*-
from plone.testing import z2
from plone.app.testing import PloneWithPackageLayer
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting

# from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE

import collective.atomrss


COLLECTIVE_ATOMRSS = PloneWithPackageLayer(
    zcml_package=collective.atomrss,
    zcml_filename='testing.zcml',
    gs_profile_id='collective.atomrss:testing',
    name='COLLECTIVE_ATOMRSS'
)

COLLECTIVE_ATOMRSS_INTEGRATION = IntegrationTesting(
    bases=(COLLECTIVE_ATOMRSS, ),
    name="COLLECTIVE_ATOMRSS_INTEGRATION"
)

COLLECTIVE_ATOMRSS_FUNCTIONAL = FunctionalTesting(
    bases=(COLLECTIVE_ATOMRSS, ),
    name="COLLECTIVE_ATOMRSS_FUNCTIONAL"
)

# COLLECTIVE_ATOMRSS_ROBOT_TESTING = FunctionalTesting(
#     bases=(
#         COLLECTIVE_ATOMRSS,
#         REMOTE_LIBRARY_BUNDLE_FIXTURE,
#         z2.ZSERVER_FIXTURE),
#     name="COLLECTIVE_ATOMRSS_ROBOT_TESTING")
