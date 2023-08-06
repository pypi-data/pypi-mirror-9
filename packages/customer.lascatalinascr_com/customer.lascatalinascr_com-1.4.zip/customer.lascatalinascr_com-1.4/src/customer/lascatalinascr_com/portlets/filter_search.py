# -*- coding: utf-8 -*-
""" Listing Filter Portlet"""

# zope imports
from Acquisition import aq_inner
from Products.CMFPlone import PloneMessageFactory as PMF
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.portlets.portlets import base
from plone.directives import form
from plone.portlets.interfaces import IPortletDataProvider
from plone.z3cform import z2
from z3c.form import button, field
from z3c.form.browser import checkbox, radio
from z3c.form.interfaces import IFormLayer
from zope import formlib, schema
from zope.interface import alsoProvides, implementer
from zope.schema.fieldproperty import FieldProperty

# starting from 0.6.0 version plone.z3cform has IWrappedForm interface
try:
    from plone.z3cform.interfaces import IWrappedForm
    HAS_WRAPPED_FORM = True
except ImportError:
    HAS_WRAPPED_FORM = False

try:
    # try to extend plone.mls.listing QuickSearch Renderer
    from plone.mls.listing.browser import listing_collection, listing_search, recent_listings
    PLONE_MLS_LISTING = True

except ImportError:
    # define fallbacks if plone.mls.listing is not installed
    PLONE_MLS_LISTING = False

# local imports
from plone.mls.listing.i18n import _

MSG_PORTLET_DESCRIPTION = _(u'This portlet shows a Ajax Filter for MLS Listings.')


#: Definition of available fields in the given ``rows``.
FIELD_ORDER = {
    'row_listing_type': [
        'listing_type',
    ],
    'row_beds': [
        'beds',
    ],

    'row_view_type': [
        'view_type',
    ],
    'row_price_sale': [
        'price_sale',
    ],
    'row_price_rent': [
        'price_rent',
    ],
    'row_pool': [
        'pool',
    ],

}


class IFilterSearchLC(form.Schema):
    """custom Form scheme for LasCatalinas QuickSearchPortlet"""

    form.widget(listing_type=checkbox.CheckBoxFieldWidget)
    listing_type = schema.Tuple(
        required=False,
        title=_(u'Listing Type'),
        value_type=schema.Choice(
            source='lasCatalinascr_com.ListingTypesVocabulary'
        ),
    )

    form.widget(beds=checkbox.CheckBoxFieldWidget)
    beds = schema.Tuple(
        required=False,
        title=_(u'Number of Bedrooms'),
        value_type=schema.Choice(
            source='lasCatalinascr_com.BedRoomsVocabulary'
        ),
    )

    form.widget(view_type=checkbox.CheckBoxFieldWidget)
    view_type = schema.Tuple(
        required=False,
        title=_(u'View'),
        value_type=schema.Choice(
            source='lasCatalinascr_com.ViewVocabulary'
        ),
    )

    form.widget(price_sale=radio.RadioFieldWidget)
    price_sale = schema.Choice(
        default='--NOVALUE--',
        required=False,
        title=_(u'Sales Price Range'),
        source='lasCatalinascr_com.PriceSaleVocabulary',
        description=_(
            u'Choose a price range for your Properties.'
        ),
    )

    form.widget(price_rent=radio.RadioFieldWidget)
    price_rent = schema.Choice(
        default='--NOVALUE--',
        required=False,
        title=_(u'Nightly Rental Price Range'),
        source='lasCatalinascr_com.PriceRentVocabulary',
        description=_(
            u'Choose a price range for your Rental.'
        ),
    )

    form.widget(pool=radio.RadioFieldWidget)
    pool = schema.Choice(
        default='--NOVALUE--',
        required=False,
        source='lasCatalinascr_com.YesNoVocabulary',
        title=_(u'Private Pool'),
        description=_(
            u'Care about a pool?'
        ),
    )


class FilterSearchForm(form.Form):
    """Filter Search Form."""

    fields = field.Fields(IFilterSearchLC)
    template = ViewPageTemplateFile('templates/searchform.pt')
    ignoreContext = True
    method = 'get'
    enable_unload_protection = False

    fields['listing_type'].widgetFactory = checkbox.CheckBoxFieldWidget
    fields['beds'].widgetFactory = checkbox.CheckBoxFieldWidget
    fields['view_type'].widgetFactory = checkbox.CheckBoxFieldWidget
    fields['price_sale'].widgetFactory = radio.RadioFieldWidget
    fields['price_rent'].widgetFactory = radio.RadioFieldWidget
    fields['pool'].widgetFactory = radio.RadioFieldWidget

    def __init__(self, context, request, data=None):
        """Customized form constructor.
            This one also takes an optional ``data`` attribute so it can be
            instantiated from within a portlet without loosing access to the
            portlet data.
        """
        super(FilterSearchForm, self).__init__(context, request)
        self.data = data

    def updateWidgets(self):
        super(FilterSearchForm, self).updateWidgets()

    @button.buttonAndHandler(PMF(u'label_search', default=u'Search'), name='search')
    def handle_search(self, action):
        """Search button."""
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

    @property
    def action(self):
        """See interfaces.IInputForm."""
        action_url = self.request.getURL()
        index = action_url.rfind('/')
        action = action_url[:index] + '/@@ajaxListingSearch'

        return action

    def _widgets(self, row):
        """Return a list of widgets that should be shown for a given row."""
        widget_data = dict(self.widgets.items())
        available_fields = FIELD_ORDER.get(row, [])
        return [widget_data.get(field, None) for field in available_fields]

    def widgets_listing_type(self):
        """Return the widgets for the row ``row_listing_type``."""
        return self._widgets('row_listing_type')

    def widgets_beds(self):
        """Return the widgets for the row ``row_beds``."""
        return self._widgets('row_beds')

    def widgets_view_type(self):
        """Return the widgets for the row ``row_view_type``."""
        return self._widgets('row_view_type')

    def widgets_price_sale(self):
        """Return the widgets for the row ``row_price_sale``."""
        return self._widgets('row_price_sale')

    def widgets_price_rent(self):
        """Return the widgets for the row ``row_price_rent``."""
        return self._widgets('row_price_rent')

    def widgets_pool(self):
        """Return the widgets for the row ``row_pool``."""
        return self._widgets('row_pool')


class IFilterSearchPortlet(IPortletDataProvider):
    """A portlet displaying a custom ajax listing search form."""
    heading = schema.TextLine(
        description=_(
            u'Custom title for the portlet (search mode). If no title is '
            u'provided, the default title is used.'
        ),
        required=False,
        title=_(u'Portlet Title (Search)'),
    )

    limit = schema.TextLine(
        description=_(
            u'How many listings per page?'
        ),
        required=False,
        title=_(u'Limit the results'),
        default=u'12'
    )

    agency_listings = schema.Bool(
        description=_(
            u'If activated, only listings of the configured agency are shown.',
        ),
        required=False,
        title=_(u'Agency Listings'),
    )


@implementer(IFilterSearchPortlet)
class Assignment(base.Assignment):
    """Filter Search Portlet Assignment."""

    heading = FieldProperty(IFilterSearchPortlet['heading'])
    try:
        limit = int(FieldProperty(IFilterSearchPortlet['limit']))
    except Exception, e:
        limit = None
    try:
        agency_listings = bool(FieldProperty(IFilterSearchPortlet['agency_listings']))
    except Exception, e:
        agency_listings = True

    title = _(u'Ajax Filter')
    mode = 'SEARCH'

    def __init__(self, heading=None, limit=None, agency_listings=None):
        self.heading = heading
        self.limit = limit
        self.agency_listings = agency_listings


class Renderer(base.Renderer):
    """Listing FilterSearch Portlet Renderer."""
    render = ViewPageTemplateFile('templates/filterportlet.pt')

    @property
    def available(self):
        """Check the portlet availability."""
        """Show on ListingCollections, Recent Listings, Listing Search """
        form = self.request.form
        show = False

        # available for ListingCollections
        if listing_collection.IListingCollection.providedBy(self.context):
            show = True
        # available for Recent Listings
        if recent_listings.IRecentListings.providedBy(self.context):
            show = True
        # available for Listing Search in Result Mode

        if listing_search.IListingSearch.providedBy(self.context) and \
                'form.buttons.search' in form.keys():
            show = True

        # available for ListingDetails
        if getattr(self.request, 'listing_id', None) is not None:
            show = True

        return show

    @property
    def title(self):
        """Return the title"""
        if self.data.heading is not None:
            return self.data.heading
        return self.data.title

    @property
    def mode(self):
        """Return the mode that we are in.
            ``SEARCH`` will be returned on valid context
            ``HIDDEN`` will be returned on invalid context
        """
        if listing_collection.IListingCollection.providedBy(self.context):
            return 'SEARCH'
        else:
            return 'HIDDEN'

    def update(self):
        z2.switch_on(self, request_layer=IFormLayer)
        self.form = FilterSearchForm(aq_inner(self.context), self.request, self.data)
        if HAS_WRAPPED_FORM:
            alsoProvides(self.form, IWrappedForm)
        self.form.update()


class AddForm(base.AddForm):
    """Add form for the Listing FilterSearch portlet."""
    form_fields = formlib.form.Fields(IFilterSearchPortlet)

    label = _(u'Add FilterSearch portlet')
    description = MSG_PORTLET_DESCRIPTION

    def create(self, data):
        assignment = Assignment()
        formlib.form.applyChanges(assignment, self.form_fields, data)
        return assignment


class EditForm(base.EditForm):
    """Edit form for the Listing FilterSearch portlet."""
    form_fields = formlib.form.Fields(IFilterSearchPortlet)

    label = _(u'Edit FilterSearch portlet')
    description = MSG_PORTLET_DESCRIPTION
