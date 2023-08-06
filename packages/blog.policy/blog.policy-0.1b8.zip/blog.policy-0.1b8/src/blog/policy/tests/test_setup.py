# -*- coding: utf-8 -*-
"""Setup/installation tests for this package."""

from plone import api
import unittest2 as unittest
from blog.policy.testing import INTEGRATION


class TestInstall(unittest.TestCase):
    """Test installation of blog.policy into Plone."""
    layer = INTEGRATION

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if blog.policy is installed with portal_quickinstaller."""
        self.assertTrue(self.installer.isProductInstalled('blog.policy'))

    def test_uninstall(self):
        """Test if blog.policy is cleanly uninstalled."""
        self.installer.uninstallProducts(['blog.policy'])
        self.assertFalse(self.installer.isProductInstalled('blog.policy'))

    # browserlayer.xml
    def test_browserlayer(self):
        """Test that IBlogPolicyLayer is registered."""
        from blog.policy.interfaces import IBlogPolicyLayer
        from plone.browserlayer import utils
        self.assertIn(IBlogPolicyLayer, utils.registered_layers())
