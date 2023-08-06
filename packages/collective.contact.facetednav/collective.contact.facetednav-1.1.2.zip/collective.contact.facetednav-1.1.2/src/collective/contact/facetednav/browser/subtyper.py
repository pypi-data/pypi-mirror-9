""" Subtyping support
"""
from zope.interface import implements
from zope.interface import alsoProvides, noLongerProvides
from zope.publisher.interfaces import NotFound

from Products.statusmessages.interfaces import IStatusMessage
from Products.Five.browser import BrowserView

from collective.contact.facetednav.browser.interfaces import IContactFacetedSubtyper
from collective.contact.facetednav.interfaces import IActionsEnabled
from collective.contact.facetednav import _


class ContactFacetedPublicSubtyper(BrowserView):
    """ Public support for subtyping objects
        view for non IPossibleFacetedNavigable objects
    """
    implements(IContactFacetedSubtyper)

    def _redirect(self, msg=''):
        """ Redirect
        """
        if self.request:
            if msg:
                IStatusMessage(self.request).addStatusMessage(msg, type='info')
            self.request.response.redirect(self.context.absolute_url())
        return msg

    @property
    def actions_enabled(self):
        return IActionsEnabled.providedBy(self.context)

    def can_enable_actions(self):
        """Can enable selection
        """
        return False

    def can_disable_actions(self):
        """Can disable selection
        """
        return False

    def enable_actions(self):
        """Enable selection
        """
        raise NotFound(self.context, 'enable_actions', self.request)

    def disable_actions(self):
        """Disable selection
        """
        raise NotFound(self.context, 'disable_actions', self.request)


class ContactFacetedSubtyper(ContactFacetedPublicSubtyper):
    """ Support for subtyping objects
        view for IPossibleFacetedNavigable objects
    """

    def can_enable_actions(self):
        """
        """
        return not self.actions_enabled

    def can_disable_actions(self):
        """
        """
        return self.actions_enabled

    def enable_actions(self):
        """
        """
        if not self.can_enable_actions():
            return self._redirect('Faceted navigation not supported')
        alsoProvides(self.context, IActionsEnabled)

        self._redirect(_('Contacts actions enabled'))

    def disable_actions(self):
        """
        """
        noLongerProvides(self.context, IActionsEnabled)
        self._redirect(_('Contacts actions disabled'))
