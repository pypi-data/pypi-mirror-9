# -*- coding: utf-8 -*-
from plone.testing import z2
from plone.app.testing import PloneWithPackageLayer
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting

from plone.app.robotframework.testing import AUTOLOGIN_LIBRARY_FIXTURE

import blog.post


BLOG_POST = PloneWithPackageLayer(
    zcml_package=blog.post,
    zcml_filename='testing.zcml',
    gs_profile_id='blog.post:testing',
    name='BLOG_POST'
)

BLOG_POST_INTEGRATION = IntegrationTesting(
    bases=(BLOG_POST, ),
    name="BLOG_POST_INTEGRATION"
)

BLOG_POST_FUNCTIONAL = FunctionalTesting(
    bases=(BLOG_POST, ),
    name="BLOG_POST_FUNCTIONAL"
)

BLOG_POST_ROBOT_TESTING = FunctionalTesting(
    bases=(BLOG_POST, AUTOLOGIN_LIBRARY_FIXTURE, z2.ZSERVER_FIXTURE),
    name="BLOG_POST_ROBOT_TESTING")


