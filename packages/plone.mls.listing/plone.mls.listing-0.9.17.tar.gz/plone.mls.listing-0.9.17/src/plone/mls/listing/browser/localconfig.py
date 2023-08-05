# -*- coding: utf-8 -*-
"""Local agency information settings."""

# zope imports
from plone.directives import form
from z3c.form import field, button
from zope.annotation.interfaces import IAnnotations
from zope.interface import alsoProvides, noLongerProvides
from zope.traversing.browser.absoluteurl import absoluteURL

# local imports
from plone.mls.listing.i18n import _
from plone.mls.listing.interfaces import (
    ILocalAgencyInfo,
    IMLSAgencyContactInformation,
    IPossibleLocalAgencyInfo,
)


CONFIGURATION_KEY = 'plone.mls.listing.localagencyinfo'


class LocalAgencyInfo(form.Form):
    """Local agency information form."""

    fields = field.Fields(IMLSAgencyContactInformation).omit('use_custom_info')
    label = _(u'Local Agency Information')
    description = _(
        u'This agency information will be used for this content item and all '
        u'possible child elements.'
    )

    def getContent(self):
        """Get the annotations with the local agency information."""
        annotations = IAnnotations(self.context)
        return annotations.get(
            CONFIGURATION_KEY,
            annotations.setdefault(CONFIGURATION_KEY, {}),
        )

    @button.buttonAndHandler(_(u'Save'))
    def handle_save(self, action):
        """Save the new configuration to the context annotations."""
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        annotations = IAnnotations(self.context)
        annotations[CONFIGURATION_KEY] = data
        self.request.response.redirect(absoluteURL(self.context, self.request))

    @button.buttonAndHandler(_(u'Cancel'))
    def handle_cancel(self, action):
        """Discard changes."""
        self.request.response.redirect(absoluteURL(self.context, self.request))


class LocalAgencyInfoStatus(object):
    """Return activation/deactivation status of the local agency infos."""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def can_activate(self):
        """Can the local agency information be activated for this context?"""
        return IPossibleLocalAgencyInfo.providedBy(self.context) and \
            not ILocalAgencyInfo.providedBy(self.context)

    @property
    def active(self):
        """Is the local agency information active for this context?"""
        return ILocalAgencyInfo.providedBy(self.context)


class LocalAgencyInfoToggle(object):
    """Toggle local agency information for the current context."""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        """Perform the toggle."""
        msg_type = 'info'

        if ILocalAgencyInfo.providedBy(self.context):
            # Deactivate local agency information.
            noLongerProvides(self.context, ILocalAgencyInfo)
            self.context.reindexObject(idxs=['object_provides', ])
            msg = _(u'Local agency information deactivated.')
        elif IPossibleLocalAgencyInfo.providedBy(self.context):
            alsoProvides(self.context, ILocalAgencyInfo)
            self.context.reindexObject(idxs=['object_provides', ])
            msg = _(u'Local agency information activated.')
        else:
            msg = _(
                u'The local agency information don\'t work with this '
                u'content type. Add \'IPossibleLocalAgencyInfo\' to the '
                u'provided interfaces to enable this feature.'
            )
            msg_type = 'error'

        self.context.plone_utils.addPortalMessage(msg, msg_type)
        self.request.response.redirect(self.context.absolute_url())
