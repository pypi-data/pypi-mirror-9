from five import grok

from z3c.form import group, field
from zope import schema
from zope.interface import invariant, Invalid, Interface, implements
from plone.supermodel import model
from plone.dexterity.content import Container

from z3c.form.form import extends

from plone.directives import dexterity, form
from plone.app.textfield import RichText
from plone.namedfile.interfaces import IImageScaleTraversable
from plone.dexterity.browser.view import DefaultView

from zope.schema.fieldproperty import FieldProperty

from collective.object import MessageFactory as _

from collective.z3cform.datagridfield import DataGridFieldFactory, IDataGridField


class DimensionListField(schema.List):
    """We need to have a unique class for the field list so that we
    can apply a custom adapter."""
    pass

class IDimension(Interface):
    part = schema.TextLine(title=u'Part', required=False)
    dimension = schema.TextLine(title=u'Dimension', required=False)
    value = schema.TextLine(title=u'Value', required=False)
    unit = schema.TextLine(title=u'Unit', required=False)
    precision = schema.TextLine(title=u'Precision', required=False)
    notes = schema.TextLine(title=u'Notes', required=False)

class IObject(form.Schema):
    text = RichText(
        title=_(u"Body text"),
        required=False
    )

    model.fieldset('collection', label=_(u'Collection'), fields=['dimension'])
    form.widget(dimension=DataGridFieldFactory)
    
    dimension = DimensionListField(title=u'Dimensions', 
        value_type=schema.Object(title=u'Dimension', schema=IDimension), 
        required=False)

class Object(Container):
    grok.implements(IObject)
    pass


class EditForm(form.EditForm):
    extends(form.EditForm)
    grok.context(IObject)
    grok.require('zope2.View')
    fields = field.Fields(IObject)

    fields['dimension'].widgetFactory = DataGridFieldFactory


class ObjectView(DefaultView):
    """ sample view class """

    pass
