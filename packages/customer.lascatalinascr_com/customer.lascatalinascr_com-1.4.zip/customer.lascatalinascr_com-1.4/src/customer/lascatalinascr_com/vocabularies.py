# -*- coding: utf-8 -*-
"""Vocabulary definitions."""

from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

from plone.mls.listing.i18n import _

LISTINGTYPE_VALUES = [
    ('rental', _(u'Rental')),
    ('sale', _(u'Sale')),
    ('home', _(u'Home')),
    ('condo', _(u'Condo')),
    ('lot', _(u'Lot')),
]

BEDROOM_VALUES = [
    (1, '1'),
    (2, '2'),
    (3, '3'),
    (4, '4'),
    (5, '5'),
    (6, '6+'),
]

VIEW_VALUES = [
    ('ocean_view', _(u'Ocean View')),
    ('oceanfront', _(u'Ocean Front')),
    ('garden_view', _(u'Garden View')),
]

PRICE_SALE_DISPLAY = [
    ('all', _(u'Show All')),
    ('250k', _(u'$250,000 - $500,000')),
    ('500k', _(u'$500,000 - $750,000')),
    ('750k', _(u'$750,000 - $1,000,000 ')),
    ('1000k', _(u'$1,000,000+')),
]

PRICE_SALE_VALUES = {
    'all': {"min": None, "max": None},
    '250k': {"min": 250000, "max": 500000},
    '500k': {"min": 500000, "max": 750000},
    '750k': {"min": 750000, "max": 1000000},
    '1000k': {"min": 1000000, "max": None}
}

PRICE_RENT_DISPLAY = [
    ('all', _(u'Show All')),
    ('150', _(u'$150 - $300')),
    ('300', _(u'$300 - $500')),
    ('500', _(u'$500 - $750')),
    ('750', _(u'$750 - $1000')),
    ('1000', _(u'$1000 - $2000+')),
]

PRICE_RENT_VALUES = {
    'all': {"min": None, "max": None},
    '150': {"min": 150 * 30, "max": 300 * 30},
    '300': {"min": 300 * 30, "max": 500 * 30},
    '500': {"min": 500 * 30, "max": 750 * 30},
    '750': {"min": 750 * 30, "max": 1000 * 30},
    '1000': {"min": 1000 * 30, "max": None}
}

YES_NO_VALUES = [
    (1, _(u'Yes')),
    (0, _(u'No')),
    ('--NOVALUE--', _(u'All'))
]


def vocabulize(myList):
    """Convert Lists into z3c form vocaularies """
    items = []
    for item in myList:
        items.append(SimpleTerm(item[0], item[0], item[1]))

    return SimpleVocabulary(items)


@implementer(IVocabularyFactory)
class ListingTypesVocabulary(object):
    def __call__(self, context):
        return vocabulize(LISTINGTYPE_VALUES)

ListingTypesVocabularyFactory = ListingTypesVocabulary()


@implementer(IVocabularyFactory)
class BedRoomsVocabulary(object):
    def __call__(self, context):
        return vocabulize(BEDROOM_VALUES)

BedRoomsVocabularyFactory = BedRoomsVocabulary()


@implementer(IVocabularyFactory)
class ViewVocabulary(object):
    def __call__(self, context):
        return vocabulize(VIEW_VALUES)

ViewVocabularyFactory = ViewVocabulary()


@implementer(IVocabularyFactory)
class PriceSaleVocabulary(object):
    def __call__(self, context):
        return vocabulize(PRICE_SALE_DISPLAY)

PriceSaleVocabularyFactory = PriceSaleVocabulary()


@implementer(IVocabularyFactory)
class PriceRentVocabulary(object):
    def __call__(self, context):
        return vocabulize(PRICE_RENT_DISPLAY)

PriceRentVocabularyFactory = PriceRentVocabulary()


@implementer(IVocabularyFactory)
class YesNoVocabulary(object):
    def __call__(self, context):
        return vocabulize(YES_NO_VALUES)

YesNoVocabularyFactory = YesNoVocabulary()
