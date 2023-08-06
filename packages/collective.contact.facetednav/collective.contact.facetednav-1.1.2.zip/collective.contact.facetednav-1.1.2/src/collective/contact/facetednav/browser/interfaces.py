from zope import schema
from zope.interface import Interface


class IContactFacetedSubtyper(Interface):
    """ Support for subtyping objects
    """

    actions_enabled = schema.Bool(u'Actions are enabled on contacts faceted navigation')

    def can_enable_actions(self):
        """Enable selection
        """

    def can_disable_actions(self):
        """Enable selection
        """

    def enable_actions(self):
        """Enable selection
        """

    def disable_actions(self):
        """Enable selection
        """
