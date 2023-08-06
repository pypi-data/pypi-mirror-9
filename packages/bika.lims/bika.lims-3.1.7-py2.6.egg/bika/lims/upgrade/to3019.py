from Acquisition import aq_inner
from Acquisition import aq_parent
from bika.lims.permissions import *


def upgrade(tool):
    portal = aq_parent(aq_inner(tool))

    wf = portal.portal_workflow
    setup = portal.portal_setup
    setup.runImportStepFromProfile('profile-bika.lims:default', 'workflow')
    wf.updateRoleMappings()

    # missing bika_arpriorities folder permission
    folder = portal.bika_setup.bika_arpriorities
    folder.manage_permission(
            ManageARPriority, 
            ['Manager', 'Site Administrator', 'LabManager', 'Owner'], 0)
    folder.reindexObject()

    return True
