from ftw.upgrade.interfaces import IRecordableHandler
from ftw.upgrade.interfaces import IUpgradeStepRecorder
from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter
from zope.interface import alsoProvides


def wrap_upgrade_step(handler, upgrade_profile, base_profile, target_version):
    def upgrade_step_wrapper(portal_setup):
        result = handler(portal_setup, upgrade_profile)

        portal = getToolByName(portal_setup, 'portal_url').getPortalObject()
        recorder = getMultiAdapter((portal, base_profile),
                                   IUpgradeStepRecorder)
        recorder.mark_as_installed(target_version)
        return result
    alsoProvides(upgrade_step_wrapper, IRecordableHandler)
    return upgrade_step_wrapper
