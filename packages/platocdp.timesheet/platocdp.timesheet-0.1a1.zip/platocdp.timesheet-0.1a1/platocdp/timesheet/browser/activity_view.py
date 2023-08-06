from five import grok
from plone.directives import dexterity, form
from platocdp.timesheet.content.activity import IActivity

grok.templatedir('templates')

class Index(dexterity.DisplayForm):
    grok.context(IActivity)
    grok.require('zope2.View')
    grok.template('activity_view')
    grok.name('view')

