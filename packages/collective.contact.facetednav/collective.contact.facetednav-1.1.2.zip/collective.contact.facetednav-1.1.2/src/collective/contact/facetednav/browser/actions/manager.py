"""Viewlet managers
"""
from zope.interface import implements
from zope.viewlet.interfaces import IViewletManager
from zope.viewlet.manager import WeightOrderedViewletManager
from AccessControl.ZopeGuards import guarded_hasattr

from collective.contact.facetednav.browser.view import ACTIONS_ENABLED_KEY


def is_available(viewlet):
    """Check if viewlet is available
    """
    if not guarded_hasattr(viewlet, 'render'):
        return False

    if hasattr(viewlet, 'available'):
        if callable(viewlet.available):
            available = viewlet.available()
        else:
            available = viewlet.available

        return available
    else:
        return True


class ConditionalViewletManager(WeightOrderedViewletManager):
    """Conditional weight ordered viewlet managers."""

    def filter(self, viewlets):
        """Sort out all viewlets which are explicit not available

        ``viewlets`` is a list of tuples of the form (name, viewlet).
        """
        return [(name, viewlet) for name, viewlet in viewlets
                if is_available(viewlet)]


class IBatchActions(IViewletManager):
    """Interface for batch actions viewlet manager
    """
    pass


class BatchActionsViewletManager(ConditionalViewletManager):
    """Batch actions viewlet manager
    """
    implements(IBatchActions)


class IActions(IViewletManager):
    pass


class ActionsViewletManager(ConditionalViewletManager):
    implements(IActions)

    def available(self):
        return self.request[ACTIONS_ENABLED_KEY]