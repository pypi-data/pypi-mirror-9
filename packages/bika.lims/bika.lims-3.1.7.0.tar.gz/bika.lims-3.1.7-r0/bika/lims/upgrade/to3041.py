from Acquisition import aq_inner
from Acquisition import aq_parent
from bika.lims.permissions import *


def upgrade(tool):
    """Added bika.lims.loader.js and bika.lims.artemplate.edit.js
    Also fix LIMS-1352 (would have been 3042, but metadata.xml is not up to date!).
    """

    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup

    # update affected tools
    setup.runImportStepFromProfile('profile-bika.lims:default', 'jsregistry')

    # LIMS-1352
    proxies = portal.bika_catalog(portal_type='Sample')
    for brain in proxies:
        sample = brain.getObject()
        sample.setSamplingWorkflowEnabled(sample.getSamplingWorkflowEnabledDefault())

    return True
