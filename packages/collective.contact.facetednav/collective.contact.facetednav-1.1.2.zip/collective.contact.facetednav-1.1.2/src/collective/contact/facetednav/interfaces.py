# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from zope.interface import Interface
from plone.theme.interfaces import IDefaultPloneLayer


class ICollectiveContactFacetednavLayer(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer."""


class IActionsEnabled(Interface):
    """Marker interface for faceted navigable directory
    where you can select contacts via checkboxes
    and run batch or contextual actions
    """

class ISettingsHandler(Interface):

    def toggle_actions_enabled(self, **kwargs):
        """ Show / hide selection inputs
        """