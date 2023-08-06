from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.config import REFERENCE_CATALOG
from bika.lims.permissions import AddStorageLocation

def upgrade(tool):
    """ Add Storage locacations to ARs and Samples.
    """
    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup

    bc = getToolByName(portal, 'bika_catalog')
    for brain in bc(portal_type='AnalysisRequest'):
        obj = brain.getObject()
        if not obj.getPriority():
            obj.setDefaultPriority()
            #obj.reindexObject()

