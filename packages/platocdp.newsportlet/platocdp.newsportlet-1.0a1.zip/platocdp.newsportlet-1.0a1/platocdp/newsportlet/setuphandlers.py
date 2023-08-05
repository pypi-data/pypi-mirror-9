from collective.grok import gs
from platocdp.newsportlet import MessageFactory as _

@gs.importstep(
    name=u'platocdp.newsportlet', 
    title=_('platocdp.newsportlet import handler'),
    description=_(''))
def setupVarious(context):
    if context.readDataFile('platocdp.newsportlet.marker.txt') is None:
        return
    portal = context.getSite()

    # do anything here
