from five import grok
from plone.directives import dexterity, form

from zope import schema
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from plone.autoform.interfaces import IFormFieldProvider
from zope.interface import alsoProvides

from zope.interface import invariant, Invalid

from z3c.form import group, field

from plone.namedfile.interfaces import IImageScaleTraversable
from plone.namedfile.field import NamedImage, NamedFile
from plone.namedfile.field import NamedBlobImage, NamedBlobFile

from plone.app.textfield import RichText

from z3c.relationfield.schema import RelationList, RelationChoice
from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.multilingualbehavior.directives import languageindependent
from collective import dexteritytextindexer

from platocdp.timesheet import MessageFactory as _
from plone.indexer import indexer

# Interface class; used to define content-type schema.

class IActivity(form.Schema, IImageScaleTraversable):
    """
    Timesheet Activity
    """

    bodyText = RichText(title=_(u'Activity Details'),
            description=_(u''),
            required=True
    )

    resource = schema.Choice(title=_(u'Resource / Staff'),
            description=_(u''),
            vocabulary='plone.app.vocabularies.Users',
            required=True
    )

    startDate = schema.Datetime(
        title=_(u"Start Date"),
        description=u'',
        required=True,
    )

    endDate = schema.Datetime(
        title=_(u"End Date"),
        description=u'',
        required=True,
    )

alsoProvides(IActivity, IFormFieldProvider)

@indexer(IActivity)
def startDate(obj):
    return obj.startDate

@indexer(IActivity)
def endDate(obj):
    return obj.endDate
