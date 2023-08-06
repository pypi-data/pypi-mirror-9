# -*- coding: utf-8 -*-
import unittest2 as unittest
from zope.event import notify
from zope.traversing.interfaces import BeforeTraverseEvent

from Products.CMFCore.utils import getToolByName

from blog.post.testing import BLOG_POST_INTEGRATION


class TestIntegration(unittest.TestCase):
    layer = BLOG_POST_INTEGRATION

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        notify(BeforeTraverseEvent(self.portal, self.request))

    def test_product_is_installed(self):
        """ Validate that our products GS profile has been run and the product
            installed
        """
        qi_tool = getToolByName(self.portal, 'portal_quickinstaller')
        pid = 'blog.post'
        installed = [p['id'] for p in qi_tool.listInstalledProducts()]
        self.assertTrue(pid in installed,
                    'package appears not to have been installed')
