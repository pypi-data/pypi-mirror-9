from Acquisition import aq_inner
from Acquisition import aq_parent
from bika.lims import logger
from bika.lims.permissions import *
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from zExceptions import BadRequest


def upgrade(tool):
    portal = aq_parent(aq_inner(tool))
    at = getToolByName(portal, 'archetype_tool')
    at.setCatalogsByType('ARPriority', ['bika_setup_catalog', ])

    return True
