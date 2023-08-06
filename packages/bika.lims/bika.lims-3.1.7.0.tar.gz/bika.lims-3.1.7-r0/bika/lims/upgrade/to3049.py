from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from bika.lims.permissions import *
from bika.lims.setuphandlers import BikaGenerator
from bika.lims import logger

def upgrade(tool):
    """ Sort by Type in instruments
    """
    portal = aq_parent(aq_inner(tool))
    bsc = getToolByName(portal, 'bika_setup_catalog', None)

    if 'getInstrumentType' not in bsc.indexes():
        bsc.addIndex('getInstrumentType', 'FieldIndex')
        bsc.addColumn('getInstrumentType')

        bsc.addIndex('getInstrumentTypeName','FieldIndex')
        bsc.addColumn('getInstrumentTypeName')

    #Del old "getType" Index, it's not used now.
    if 'getType' in bsc.indexes():
        bsc.delIndex('getType')
    if 'getType' in bsc.indexes():
        bsc.delColumn('getType')

    setup = portal.portal_setup

    logger.info("Reindex added indexes in bika_setup_catalog")
    bsc.manage_reindexIndex(
        ids=['getInstrumentType', 'getInstrumentTypeName', ])

    return True
