# -*- coding: utf-8 -*-
"""Base module for unittesting."""
import os

from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import login
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.testing import z2

import unittest2 as unittest

from zope.interface import alsoProvides
from eea.facetednavigation.subtypes.interfaces import IFacetedNavigable
import collective.contact.facetednav
import collective.contact.core


class CollectiveContactFacetednavLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        """Set up Zope."""
        # Load ZCML
        self.loadZCML(package=collective.contact.facetednav,
                      name='testing.zcml')
        z2.installProduct(app, 'collective.contact.facetednav')
        self.loadZCML(package=collective.contact.core,
                      name='testing.zcml')

    def setUpPloneSite(self, portal):
        """Set up Plone."""
        # Install into Plone site using portal_setup
        applyProfile(portal, 'collective.contact.core:testing')
        # insert some test data
        applyProfile(portal, 'collective.contact.core:test_data')
        applyProfile(portal, 'collective.contact.facetednav:default')
        alsoProvides(portal.mydirectory, IFacetedNavigable)
        portal.mydirectory.unrestrictedTraverse('@@faceted_exportimport')._import_xml(
            import_file=open(os.path.dirname(__file__) + '/tests/contacts-faceted.xml'))

        # Login and create some test content
        setRoles(portal, TEST_USER_ID, ['Manager'])
        login(portal, TEST_USER_NAME)
        portal.invokeFactory('Folder', 'folder')

        # Commit so that the test browser sees these objects
        portal.portal_catalog.clearFindAndRebuild()
        import transaction
        transaction.commit()

    def tearDownZope(self, app):
        """Tear down Zope."""
        z2.uninstallProduct(app, 'collective.contact.facetednav')


FIXTURE = CollectiveContactFacetednavLayer(
    name="FIXTURE"
    )

INTEGRATION = IntegrationTesting(
    bases=(FIXTURE,),
    name="INTEGRATION"
    )

FUNCTIONAL = FunctionalTesting(
    bases=(FIXTURE,),
    name="FUNCTIONAL"
    )


class IntegrationTestCase(unittest.TestCase):
    """Base class for integration tests."""

    layer = INTEGRATION

    def setUp(self):
        super(IntegrationTestCase, self).setUp()
        self.portal = self.layer['portal']


class FunctionalTestCase(unittest.TestCase):
    """Base class for functional tests."""

    layer = FUNCTIONAL
