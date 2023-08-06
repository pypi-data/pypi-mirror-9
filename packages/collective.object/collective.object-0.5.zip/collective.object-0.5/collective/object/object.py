#!/usr/bin/python
# -*- coding: utf-8 -*-

from five import grok

from z3c.form import group, field
from zope import schema
from zope.interface import invariant, Invalid, Interface, implements
from plone.supermodel import model
from plone.dexterity.content import Container
from zope.component import getMultiAdapter
from z3c.form.form import extends
from z3c.form.browser.textlines import TextLinesFieldWidget

from plone.directives import dexterity, form
from plone.app.textfield import RichText
from plone.namedfile.interfaces import IImageScaleTraversable
from plone.dexterity.browser.view import DefaultView

from zope.schema.fieldproperty import FieldProperty

from collective.object import MessageFactory as _

from collective.z3cform.datagridfield import DataGridFieldFactory, IDataGridField
from collective.leadmedia.interfaces import ICanContainMedia
from collective import dexteritytextindexer


class IObject(form.Schema):
    text = RichText(
        title=_(u"Body text"),
        required=False
    )

    # Searchable fields
    dexteritytextindexer.searchable('institution_name')
    dexteritytextindexer.searchable('administrative_name')
    dexteritytextindexer.searchable('collection')
    dexteritytextindexer.searchable('object_number')
    dexteritytextindexer.searchable('rec_type')
    dexteritytextindexer.searchable('tot_number')
    dexteritytextindexer.searchable('copy_number')
    dexteritytextindexer.searchable('edition')
    dexteritytextindexer.searchable('distinguish_features')
    dexteritytextindexer.searchable('object_category')
    dexteritytextindexer.searchable('object_name')
    dexteritytextindexer.searchable('other_name')
    
    #
    # Define fieldsets
    #

    model.fieldset('identification', label=_(u'Identification'), 
        fields=['institution_name', 'administrative_name', 'collection', 'object_number', 'rec_type', 'part', 'tot_number', 'copy_number', 'edition', 'distinguish_features', 
                'object_category', 'object_name', 'other_name']
    )

    #
    # Declare widgets
    #
    #form.widget(dimension=DataGridFieldFactory)


    #
    # Identification tab
    #

    # Identification
    institution_name = schema.TextLine(title=_(u'Institution name'), required=False)
    administrative_name = schema.TextLine(title=_(u'Administrative name'), required=False)
    collection = schema.TextLine(title=_(u'Collection'), required=False)
    object_number = schema.TextLine(title=_(u'Object number'), required=False)
    rec_type = schema.TextLine(title=_(u'Rec. type'), required=False)
    part = schema.TextLine(title=_(u'Part'), required=False)
    tot_number = schema.TextLine(title=_(u'Tot. Number'), required=False)
    copy_number = schema.TextLine(title=_(u'Copy number'), required=False)
    edition = schema.TextLine(title=_(u'Edition'), required=False)
    distinguish_features = schema.TextLine(title=_(u'Distinguish features'), required=False)

    # Object name
    object_category = schema.TextLine(title=_(u'Object Category'), required=False)
    object_name = schema.TextLine(title=_(u'Object name'), required=False)
    other_name = schema.TextLine(title=_(u'Other name'), required=False)


class Object(Container):
    grok.implements(IObject)
    pass


#class EditForm(form.EditForm):
#    extends(form.EditForm)
#    grok.context(IObject)
#    grok.require('zope2.View')
#    fields = field.Fields(IObject)



class ObjectView(DefaultView):
    """ sample view class """

    def trim_white_spaces(self, text):
        if text != "" and text != None:
            if len(text) > 0:
                if text[0] == " ":
                    text = text[1:]
                if len(text) > 0:
                    if text[-1] == " ":
                        text = text[:-1]
                return text
            else:
                return ""
        else:
            return ""

    def create_author_name(self, value):
        comma_split = value.split(",")

        for i in range(len(comma_split)):       
            name_split = comma_split[i].split('(')
            
            raw_name = name_split[0]
            name_split[0] = self.trim_white_spaces(raw_name)
            name_artist = name_split[0]
            
            name_artist_link = '<a href="/'+self.context.language+'/search?SearchableText=%s">%s</a>' % (name_artist, name_artist)
            name_split[0] = name_artist_link

            if len(name_split) > 1:
                if len(name_split[1]) > 0:
                    name_split[0] = name_artist_link + " "
        
            comma_split[i] = '('.join(name_split)

        _value = ", ".join(comma_split)

        return _value

    def create_materials(self, value):
        materials = value.split(',')
        _value = ""
        for i, mat in enumerate(materials):
            if i == (len(materials)-1):
                _value += '<a href="/'+self.context.language+'/search?SearchableText=%s">%s</a>' % (mat, mat)
            else:
                _value += '<a href="/'+self.context.language+'/search?SearchableText=%s">%s</a>, ' % (mat, mat)

        return _value

    def getSearchableValue(self, name, value):
        _value = ""

        if (name == 'artist') or (name == 'author'):
            _value = self.create_author_name(value)
        elif (name == 'material') or (name == 'technique'):
            _value = self.create_materials(value)
        else:
            _value = '<a href="/'+self.context.language+'/search?SearchableText=%s">%s</a>' % (value, value)

        return _value

    def getFBdetails(self):
        item = self.context
        
        state = getMultiAdapter(
                (item, self.request),
                name=u'plone_context_state')

        # Check view type
        view_type = state.view_template_id()

        obj = ICanContainMedia(item)

        details = {}
        details["title"] = item.Title()
        details["type"] = "article"
        details["site_name"] = "Teylers Museum"
        details["url"] = item.absolute_url()
        details["description"] = item.Description()
        details["double_image"] = ""
        details["image"] = ""
        
        if view_type == "instruments_view":
            if hasattr(item, 'slideshow'):
                catalog = getToolByName(self.context, 'portal_catalog')
                slideshow = item['slideshow']
                path = '/'.join(slideshow.getPhysicalPath())
                results = catalog.searchResults(path={'query': path, 'depth': 1, 'portal_type': 'Image'}, sort_on='sortable_title')
                if len(results) > 0:
                    lead_image = results[0]
                    if lead_image.portal_type == "Image":
                        details["image"] = lead_image.getObject().absolute_url()+"/@@images/image/large"
                else:
                    details["image"] = ""
                

        if details["image"] == "":
            if obj.hasMedia():
                image = obj.getLeadMedia()
                details["image"] = image.absolute_url()+"/@@images/image/large"
                
                if view_type == "double_view":
                    if hasattr(item, 'slideshow'):
                        slideshow = item['slideshow']
                        if len(slideshow.objectIds()) > 1:
                            double_image = slideshow[slideshow.objectIds()[1]]
                            if double_image.portal_type == "Image":
                                details["double_image"] = double_image.absolute_url()+"/@@images/image/large"
            else:
                details["image"] = ""

        return details
