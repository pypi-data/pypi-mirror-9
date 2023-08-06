from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase


class BatchActionBase(ViewletBase):
    index = ViewPageTemplateFile('batchaction.pt')
    klass = 'context' # css class
    onclick = None # onclick action. Must be set.
    name = None # action id. Must be set.
    weight = 1000 # info for actions order
    # if True the action is activated when several elements are selected
    multiple_selection = False

    def available(self):
        return True


class ActionBase(ViewletBase):
    index = ViewPageTemplateFile('action.pt')
    klass = None # css class
    onclick = None # onclick action. Must be set.
    icon = None # action icon. Must be set.
    name = None # action id. Must be set.
    weight = 1000 # info for actions order

    def available(self):
        return True
