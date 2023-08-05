# -*- coding: utf-8 -*-
"""Setup handlers for plone.mls.listing."""

# python imports
import pkg_resources

# zope imports
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from zope.component import getUtility

LISTING_TYPE = 'plone.mls.listing.listing'
ADD_ONS = [
    'ps.plone.fotorama',
]


def setup_article(context):
    """Set up raptus.article."""
    if not context.readDataFile('plone.mls.listing_various.txt'):
        return

    site = getUtility(IPloneSiteRoot)
    quickinstaller = getToolByName(site, 'portal_quickinstaller')
    portal_types = getToolByName(site, 'portal_types')
    if quickinstaller.isProductInstalled('raptus.article.core'):
        article = portal_types.get('Article', None)
        if article is None:
            return
        if LISTING_TYPE not in article.allowed_content_types:
            article.allowed_content_types += (LISTING_TYPE, )


def install_add_ons(context):
    """Install additional available add-ons."""
    if not context.readDataFile('plone.mls.listing_various.txt'):
        return

    site = getUtility(IPloneSiteRoot)
    quickinstaller = getToolByName(site, 'portal_quickinstaller')

    for item in ADD_ONS:
        try:
            pkg_resources.get_distribution(item)
        except pkg_resources.DistributionNotFound:
            continue

        # Only install add-ons which are not installed yet.
        if not quickinstaller.isProductInstalled(item):
            if quickinstaller.isProductInstallable(item):
                quickinstaller.installProduct(item)
