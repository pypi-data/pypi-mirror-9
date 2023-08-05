# -*- coding: utf-8 -*-
"""Test plone.mls.listing Agent Contact portlet."""

# python imports
import unittest2 as unittest

# zope imports
from plone.app.portlets.storage import PortletAssignmentMapping
from plone.app.testing import TEST_USER_ID, setRoles
from plone.portlets import interfaces
from zope.component import getMultiAdapter, getUtility
from zope.interface import Invalid

# local imports
from plone.mls.listing.portlets import agent_contact
from plone.mls.listing.testing import PLONE_MLS_LISTING_INTEGRATION_TESTING


class TestAgentContactPortlet(unittest.TestCase):
    """Test Case for the Agent Contact portlet."""

    layer = PLONE_MLS_LISTING_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ('Manager', ))
        self.portlet = getUtility(interfaces.IPortletType,
                                  name='portlets.AgentContact')

    def test_portlet_type_registered(self):
        self.assertEqual(self.portlet.addview, 'portlets.AgentContact')

    def test_interfaces(self):
        portlet = agent_contact.Assignment()
        self.assertTrue(interfaces.IPortletAssignment.providedBy(portlet))
        self.assertTrue(
            interfaces.IPortletDataProvider.providedBy(portlet))

    def test_invoke_add_view(self):
        mapping = self.portal.restrictedTraverse(
            '++contextportlets++plone.leftcolumn')
        for item in mapping.keys():
            del mapping[item]
        addview = mapping.restrictedTraverse('+/' + self.portlet.addview)
        addview.createAndAdd(data={})
        self.assertEqual(len(mapping), 1)
        self.assertTrue(isinstance(mapping.values()[0],
                                   agent_contact.Assignment))

    def test_invoke_edit_view(self):
        request = self.layer['request']
        mapping = PortletAssignmentMapping()
        mapping['foo'] = agent_contact.Assignment()
        editview = getMultiAdapter((mapping['foo'], request), name='edit')
        self.assertIsInstance(editview, agent_contact.EditForm)

    def test_renderer(self):
        request = self.layer['request']
        view = self.portal.restrictedTraverse('@@plone')
        manager = getUtility(
            interfaces.IPortletManager,
            name='plone.rightcolumn',
            context=self.portal,
        )
        assignment = agent_contact.Assignment()
        renderer = getMultiAdapter(
            (self.portal, request, view, manager, assignment),
            interfaces.IPortletRenderer)
        self.assertIsInstance(renderer, agent_contact.Renderer)


class TestRenderer(unittest.TestCase):
    """Test Case for the Agent Contact portlet renderer."""

    layer = PLONE_MLS_LISTING_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ('Manager', ))

    def renderer(self, context=None, request=None, view=None, manager=None,
                 assignment=None):
        context = context or self.portal
        request = request or self.layer['request']
        view = view or self.portal.restrictedTraverse('@@plone')
        manager = manager or getUtility(interfaces.IPortletManager,
                                        name='plone.rightcolumn',
                                        context=self.portal)
        assignment = assignment or agent_contact.Assignment()

        return getMultiAdapter((context, request, view, manager, assignment),
                               interfaces.IPortletRenderer)

    def test_title(self):
        r = self.renderer(
            context=self.portal, assignment=agent_contact.Assignment())
        self.assertEqual('Agent Contact', r.title)

    def test_custom_title(self):
        r = self.renderer(
            context=self.portal, assignment=agent_contact.Assignment(
                heading=u'My Title'))
        self.assertEqual('My Title', r.title)

    def test_spam_setting(self):
        r = self.renderer(
            context=self.portal,
            assignment=agent_contact.Assignment(reject_links=True),
        )
        self.assertTrue(r.data.reject_links)

        r = self.renderer(
            context=self.portal,
            assignment=agent_contact.Assignment(reject_links=False),
        )
        self.assertFalse(r.data.reject_links)


class TestValidators(unittest.TestCase):
    """Test Case for validators."""

    def _callFUT(self, value):
        from plone.mls.listing.portlets.agent_contact import contains_nuts
        return contains_nuts(value)

    def _callFUTemail(self, value):
        from plone.mls.listing.portlets.agent_contact import validate_email
        return validate_email(value)

    def test_no_value_spam(self):
        self.assertTrue(self._callFUT(None))
        self.assertTrue(self._callFUT(u''))

    def test_no_urls(self):
        value = 'foobar'
        self.assertTrue(self._callFUT(value))
        value = """This is a multi line text.

        Line 3.
        Line 4.
        Still no url.
        """
        self.assertTrue(self._callFUT(value))

    def test_urls(self):
        value = 'Text with http://google.com url.'
        self.assertRaises(Invalid, self._callFUT, value)

        value = """This is a multi line text.

        Line 3.
        Line 4.
        Link to https://google.com.
        Another line.
        """
        self.assertRaises(Invalid, self._callFUT, value)

    def test_no_value_mail(self):
        self.assertTrue(self._callFUTemail(None))
        self.assertTrue(self._callFUTemail(u''))

    def test_valid_emails(self):
        value = 'test@propertyshelf.com'
        self.assertTrue(self._callFUTemail(value))
        value = 'test123.tester@propertyshelf.com'
        self.assertTrue(self._callFUTemail(value))

    def test_not_valid(self):
        value = 't!st@propertyshelf.com'
        self.assertRaises(Invalid, self._callFUTemail, value)

        value = 'test.propertyshelf.com'
        self.assertRaises(Invalid, self._callFUTemail, value)

        value = '@propertyshelf.com'
        self.assertRaises(Invalid, self._callFUTemail, value)
