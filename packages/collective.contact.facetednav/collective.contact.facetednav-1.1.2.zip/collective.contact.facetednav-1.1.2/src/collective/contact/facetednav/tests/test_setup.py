# -*- coding: utf-8 -*-
"""Setup/installation tests for this package."""
import json

from zope.interface.declarations import alsoProvides
from plone import api

from plone.app.testing.helpers import login
from plone.app.testing.interfaces import TEST_USER_NAME

from eea.facetednavigation.interfaces import IPossibleFacetedNavigable

from collective.contact.facetednav.testing import IntegrationTestCase
from collective.contact.facetednav.interfaces import ICollectiveContactFacetednavLayer


class TestInstall(IntegrationTestCase):
    """Test installation of collective.contact.facetednav into Plone."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if collective.contact.facetednav is installed with portal_quickinstaller."""
        self.assertTrue(self.installer.isProductInstalled('collective.contact.facetednav'))
        self.assertTrue('mydirectory' in self.portal)
        self.assertTrue(IPossibleFacetedNavigable.providedBy(self.portal.mydirectory))

    def test_uninstall(self):
        """Test if collective.contact.facetednav is cleanly uninstalled."""
        self.installer.uninstallProducts(['collective.contact.facetednav'])
        self.assertFalse(self.installer.isProductInstalled('collective.contact.facetednav'))

    # browserlayer.xml
    def test_browserlayer(self):
        """Test that ICollectiveContactFacetednavLayer is registered."""
        from plone.browserlayer import utils
        self.failUnless(ICollectiveContactFacetednavLayer in utils.registered_layers())

    def test_subtyper(self):
        login(self.portal, TEST_USER_NAME)
        directory = self.portal.mydirectory
        alsoProvides(self.portal.REQUEST, ICollectiveContactFacetednavLayer)
        subtyper = directory.unrestrictedTraverse('@@contact_faceted_subtyper')
        subtyper.enable_actions()
        self.assertTrue(subtyper.actions_enabled)
        self.assertFalse(subtyper.can_enable_actions())
        self.assertTrue(subtyper.can_disable_actions())
        self.assertTrue(directory.unrestrictedTraverse('@@faceted_query').actions_enabled())

        subtyper.disable_actions()
        self.assertFalse(subtyper.actions_enabled)
        self.assertTrue(subtyper.can_enable_actions())
        self.assertFalse(subtyper.can_disable_actions())
        self.assertFalse(directory.unrestrictedTraverse('@@faceted_query').actions_enabled())

    def test_json_contacts(self):
        login(self.portal, TEST_USER_NAME)
        alsoProvides(self.portal.REQUEST, ICollectiveContactFacetednavLayer)
        directory = self.portal.mydirectory

        self.portal.REQUEST.form['type'] = 'organization'
        json_contacts = json.loads(directory.unrestrictedTraverse('@@json-contacts')())
        self.assertEqual(len(json_contacts), 7)
        self.assertTrue(json_contacts[0].has_key('id'))
        self.assertEqual(json_contacts[0]['path'], '/plone/mydirectory/armeedeterre')

        self.portal.REQUEST.form['type'] = 'held_position'
        json_contacts = json.loads(directory.unrestrictedTraverse('@@json-contacts')())
        self.assertEqual(len(json_contacts), 4)
        self.assertEqual(json_contacts[0]['path'], '/plone/mydirectory/degaulle/adt')

    def test_delete_action(self):
        login(self.portal, TEST_USER_NAME)
        directory = self.portal.mydirectory

        self.assertIn('rambo', directory)
        self.portal.REQUEST.form['uids'] = [directory.rambo.UID()]
        delete_view = directory.unrestrictedTraverse('@@delete_selection')
        delete_view()
        self.assertNotIn('rambo', directory)
