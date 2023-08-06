from Acquisition import aq_parent, aq_inner


def upgrade(tool):
    portal = aq_parent(aq_inner(tool))

    # Fix Analysis Services IMM incoherences
    for service in portal.bika_setup.bika_analysisservices.objectValues('AnalysisService'):
        if (service.getInstrumentEntryOfResults() == False):
            # Remove any assigned instrument
            service.setInstruments([])
            service.setInstrument(None)

        if (service.getManualEntryOfResults() == False):
            # Remove any assigned manual method
            service.setMethods([])
            service.set_Method(None)

        service.reindexObject()

    return True
