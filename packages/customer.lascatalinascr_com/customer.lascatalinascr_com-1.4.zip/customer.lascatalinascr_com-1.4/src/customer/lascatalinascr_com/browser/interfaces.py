# -*- coding: utf-8 -*-

from zope.interface import Interface
from plone.mls.listing.browser.interfaces import IListingSpecific


class ICustomerLascatalinascrComLayer(Interface):
    """Marker interface for the Browserlayer."""


class ILascatalinascrListingLayer(IListingSpecific):
    """Add a custom Listing Layer"""
