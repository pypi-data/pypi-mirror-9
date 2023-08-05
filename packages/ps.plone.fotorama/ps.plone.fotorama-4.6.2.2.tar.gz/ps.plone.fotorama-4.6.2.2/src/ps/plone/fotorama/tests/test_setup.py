# -*- coding: utf-8 -*-
"""Test Setup of ps.plone.fotorama."""

# python imports
try:
    import unittest2 as unittest
except ImportError:
    import unittest

# zope imports
from plone import api
from plone.browserlayer.utils import registered_layers

# local imports
from ps.plone.fotorama.config import PROJECTNAME
from ps.plone.fotorama.testing import INTEGRATION_TESTING


class TestSetup(unittest.TestCase):
    """Validate setup process for ps.plone.fotorama."""

    layer = INTEGRATION_TESTING

    def setUp(self):
        """Additional test setup."""
        self.portal = self.layer['portal']

    def test_product_is_installed(self):
        """Validate that our product is installed."""
        qi = self.portal.portal_quickinstaller
        self.assertTrue(qi.isProductInstalled(PROJECTNAME))

    def test_addon_layer(self):
        """Validate that the browserlayer for our product is installed."""
        layers = [l.getName() for l in registered_layers()]
        self.assertIn('IPloneFotoramaLayer', layers)

    def test_css_registered(self):
        """Validate that the CSS files are registered properly."""
        css_registry = self.portal['portal_css']
        stylesheets_ids = css_registry.getResourceIds()
        self.assertIn(
            '++resource++ps.plone.fotorama/fotorama.css',
            stylesheets_ids,
        )

    def test_js_registered(self):
        """Validate that the JS files are registered properly."""
        js_registry = self.portal['portal_javascripts']
        javascript_ids = js_registry.getResourceIds()
        self.assertIn(
            '++resource++ps.plone.fotorama/fotorama.js',
            javascript_ids,
        )


class UninstallTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        """Additional test setup."""
        self.portal = self.layer['portal']

        qi = self.portal.portal_quickinstaller
        with api.env.adopt_roles(['Manager']):
            qi.uninstallProducts(products=[PROJECTNAME])

    def test_product_is_uninstalled(self):
        """Validate that our product is uninstalled."""
        qi = self.portal.portal_quickinstaller
        self.assertFalse(qi.isProductInstalled(PROJECTNAME))

    def test_addon_layer_removed(self):
        """Validate that the browserlayer is removed."""
        layers = [l.getName() for l in registered_layers()]
        self.assertNotIn('IPloneFotoramaLayer', layers)
