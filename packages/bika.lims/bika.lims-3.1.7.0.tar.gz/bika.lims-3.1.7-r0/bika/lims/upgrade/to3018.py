from Acquisition import aq_inner
from Acquisition import aq_parent
from bika.lims import logger
from bika.lims.permissions import *
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from zExceptions import BadRequest


def upgrade(tool):
    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup
    typestool = getToolByName(portal, 'portal_types')

    # Add the object to bika_setup
    try:
        portal.bika_setup.manage_delObjects('bika_arpriorities')
    except BadRequest:
        logger.info("Folder doesn't exist")
        
    try:
        typestool.constructContent(type_name="ARPriorities",
                               container=portal.bika_setup,
                               id='bika_arpriorities',
                               title='AR Priorities')
        obj = portal.bika_setup.bika_arpriorities
        obj.unmarkCreationFlag()
        obj.reindexObject()
    except BadRequest:
        # folder already exists
        pass

    return True
