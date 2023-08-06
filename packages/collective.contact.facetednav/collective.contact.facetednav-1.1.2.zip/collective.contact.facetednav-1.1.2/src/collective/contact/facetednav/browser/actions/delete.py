from zope.i18n import translate

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from plone.app.linkintegrity.interfaces import ILinkIntegrityInfo
from plone.app.linkintegrity.exceptions import LinkIntegrityNotificationException

from collective.contact.facetednav.browser.view import json_output
from collective.contact.facetednav.browser.actions.base import (
    ActionBase, BatchActionBase)
from collective.contact.facetednav import _


class DeleteBatchAction(BatchActionBase):

    label = _("Delete selected contacts")
    name = 'delete'
    klass = 'destructive'
    weight = 500

    @property
    def onclick(self):
        return 'contactfacetednav.delete_selection("%s")' % translate(
                    _('confirm_delete_selection',
                      default=u"Are you sure you want to remove $num selected content(s) ?"),
                    context=self.request)


class DeleteSelection(BrowserView):
    weight = 500

    @json_output
    def delete(self):
        uids = self.request['uids']
        ctool = getToolByName(self.context, 'portal_catalog')
        mtool = getToolByName(self.context, 'portal_membership')
        brains = ctool(UID=uids)
        fails = []
        success = 0
        integrity_info = ILinkIntegrityInfo(self.request)
        for b in brains:
            obj = b.getObject()
            integrity_info.addDeletedItem(obj)
            if not mtool.checkPermission('Delete objects', obj):
                fails.append(translate(_(u"Unauthorized: ${path}",
                                         mapping={'path': b.getPath()}),
                                       context=self.request))
            else:
                try:
                    parent = obj.getParentNode()
                    parent.manage_delObjects([obj.getId()])
                except LinkIntegrityNotificationException:
                    pass
                finally:
                    success += 1

        IStatusMessage(self.request).add(_("msg_objects_deleted",
                                           default="${num} object(s) deleted",
                                           mapping={'num': success}))
        if fails:
            IStatusMessage(self.request).add(
                      _("msg_objects_delete_failed",
                        default="${num} object(s) were not deleted : ${fails}",
                        mapping={'num': len(fails), 'fails': ", ".join(fails)}),
                      'error')


class DeleteAction(ActionBase):

    klass = 'delete-contact'
    name = 'delete-contact'
    icon = 'delete_icon.png'
    title = _(u"Delete this contact")

    def url(self):
        return "%s/delete_confirmation" % self.context.absolute_url()