from collective.grok import gs
from platocdp.timesheet import MessageFactory as _

@gs.importstep(
    name=u'platocdp.timesheet', 
    title=_('platocdp.timesheet import handler'),
    description=_(''))
def setupVarious(context):
    if context.readDataFile('platocdp.timesheet.marker.txt') is None:
        return
    portal = context.getSite()

    # do anything here
