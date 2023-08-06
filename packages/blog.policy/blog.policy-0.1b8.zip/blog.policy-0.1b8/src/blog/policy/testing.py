# -*- coding: utf-8 -*-
"""Base module for unittesting."""

from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneWithPackageLayer

from plone.app.robotframework.testing import AUTOLOGIN_LIBRARY_FIXTURE
from plone.testing import z2

import blog.policy


FIXTURE = PloneWithPackageLayer(
    name="FIXTURE",
    zcml_filename="testing.zcml",
    zcml_package=blog.policy,
    additional_z2_products=('',),
    gs_profile_id="blog.policy:testing"
)

INTEGRATION = IntegrationTesting(
    bases=(FIXTURE,),
    name="INTEGRATION"
)


FUNCTIONAL = FunctionalTesting(
    bases=(FIXTURE,),
    name="FUNCTIONAL"
)


ACCEPTANCE = FunctionalTesting(bases=(FIXTURE,
                                      AUTOLOGIN_LIBRARY_FIXTURE,
                                      z2.ZSERVER_FIXTURE),
                               name="ACCEPTANCE")
