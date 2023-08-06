# -*- coding: utf-8 -*-
import unittest2 as unittest
from plone.browserlayer import utils
from zope.event import notify
from zope.traversing.interfaces import BeforeTraverseEvent

from Products.CMFCore.utils import getToolByName

from collective.atomrss.interfaces import ICollectiveAtomrssLayer
from collective.atomrss.testing import COLLECTIVE_ATOMRSS_INTEGRATION
from Products.CMFPlone.interfaces.syndication import IFeedSettings


class TestSetup(unittest.TestCase):
    layer = COLLECTIVE_ATOMRSS_INTEGRATION

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        notify(BeforeTraverseEvent(self.portal, self.request))
        self.pid = 'collective.atomrss'

    def test_product_is_installed(self):
        """ Validate that our products GS profile has been run and the product
            installed
        """
        qi_tool = getToolByName(self.portal, 'portal_quickinstaller')
        installed = [p['id'] for p in qi_tool.listInstalledProducts()]
        self.assertTrue(
            self.pid in installed,
            'package appears not to have been installed')

    def test_browserlayer(self):
        """Test that ICollectiveAtomrssLayer is registered."""
        self.assertIn(ICollectiveAtomrssLayer, utils.registered_layers())

    def test_uninstall(self):
        """Test if collective.atomrss is cleanly uninstalled."""
        qi_tool = getToolByName(self.portal, 'portal_quickinstaller')
        qi_tool.uninstallProducts([self.pid])
        self.assertFalse(qi_tool.isProductInstalled(self.pid))
        self.assertNotIn(ICollectiveAtomrssLayer, utils.registered_layers())
