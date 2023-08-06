from five import grok
from Products.CMFCore.interfaces import IContentish
from platocdp.timesheet.content.activity import IActivity

grok.templatedir('templates')

class TimesheetListing(grok.View):
    grok.context(IContentish)
    grok.name('timesheetlisting')
    grok.require('zope2.View')
    grok.template('timesheetlisting')

    def timesheets(self):
        result = []
        for key, item in self.context.items():
            if IActivity.providedBy(item):
                result.append({
                    'start': item.startDate,
                    'end': item.endDate,
                    'title': item.Title,
                    'resource': item.resource,
                    'url': item.absolute_url()
                })

        return result
