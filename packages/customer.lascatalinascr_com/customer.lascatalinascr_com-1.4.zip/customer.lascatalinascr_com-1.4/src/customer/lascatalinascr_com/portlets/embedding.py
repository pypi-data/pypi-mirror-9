# -*- coding: utf-8 -*-

from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implementer
from zope import formlib, schema
from zope.schema.fieldproperty import FieldProperty

# local imports
from plone.mls.listing.i18n import _

MSG_PORTLET_DESCRIPTION = _(u'This portlet let include embedding text.')


class IEmbeddingPortlet(IPortletDataProvider):
    """ A embedding portlet """
    heading = schema.TextLine(
        description=_(u'Portlet Title'),
        required=False,
        title=_(u'Embedding Title'),
    )

    plugin_code = schema.Text(
        description=_(u'Please enter the Embedding Code.'),
        required=False,
        title=_(u'Embedding Code'),
    )


@implementer(IEmbeddingPortlet)
class Assignment(base.Assignment):
    """Embedding Portlet Assignment."""

    heading = FieldProperty(IEmbeddingPortlet['heading'])
    plugin_code = FieldProperty(IEmbeddingPortlet['plugin_code'])
    title = _(u'Embedding Portlet')

    def __init__(self, heading=None, plugin_code=None):
        self.heading = heading
        self.plugin_code = plugin_code


class Renderer(base.Renderer):
    """Embedding Portlet Renderer."""
    render = ViewPageTemplateFile('templates/embedding.pt')

    @property
    def available(self):
        """Check the portlet availability."""
        """Show on ListingDetails"""
        show = False
        # available for ListingDetails
        if getattr(self.request, 'listing_id', None) is not None:
            show = True
        return show

    @property
    def title(self):
        """Return the title"""
        if self.data.heading is not None:
            return self.data.heading
        else:
            return False

    @property
    def get_code(self):
        """Get Plugin Code"""
        return self.data.plugin_code


class AddForm(base.AddForm):
    """Add form for the Listing Related Listing Portlet."""
    form_fields = formlib.form.Fields(IEmbeddingPortlet)

    label = _(u'Add Embedding Portlet')
    description = MSG_PORTLET_DESCRIPTION

    def create(self, data):
        assignment = Assignment()
        formlib.form.applyChanges(assignment, self.form_fields, data)
        return assignment


class EditForm(base.EditForm):
    """Edit form for the Listing FilterSearch portlet."""
    form_fields = formlib.form.Fields(IEmbeddingPortlet)

    label = _(u'Edit Embedding portlet')
    description = MSG_PORTLET_DESCRIPTION
