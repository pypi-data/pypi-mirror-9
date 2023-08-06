# -*- coding: utf-8 -*-
"""Migration Steps for the customer.lascatalinas_cr"""

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from zope.component import getUtility

PROFILE_ID = 'profile-customer.lascatalinascr_com:default'


def migrate_to_1001(context):
    """Migrate from 1000 to 1001.

    * Register JS resources.
    * Register portlets.
    * Register css resources.
    """
    site = getUtility(IPloneSiteRoot)
    setup = getToolByName(site, 'portal_setup')
    setup.runImportStepFromProfile(PROFILE_ID, 'jsregistry')
    setup.runImportStepFromProfile(PROFILE_ID, 'cssregistry')
    setup.runImportStepFromProfile(PROFILE_ID, 'portlets')


def migrate_to_1002(context):
    """Migrate from 1001 to 1002.
    * Register embedding portlet.
    """
    site = getUtility(IPloneSiteRoot)
    setup = getToolByName(site, 'portal_setup')
    setup.runImportStepFromProfile(PROFILE_ID, 'portlets')
