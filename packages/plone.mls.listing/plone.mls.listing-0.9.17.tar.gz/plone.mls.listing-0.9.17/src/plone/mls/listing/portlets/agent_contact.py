# -*- coding: utf-8 -*-
"""Agent Contact Portlet."""

# python imports
from email import message_from_string
import copy
import re

# zope imports
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as PMF
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.portlets.portlets import base
from plone.directives import form
from plone.portlets.interfaces import IPortletDataProvider
from plone.z3cform import z2
from z3c.form import button, field, validator
from z3c.form.interfaces import HIDDEN_MODE, IFormLayer
from zope import formlib, schema
from zope.interface import Interface, Invalid, alsoProvides, implementer
from zope.schema.fieldproperty import FieldProperty

# local imports
from plone.mls.listing.browser.interfaces import IListingDetails
from plone.mls.listing.i18n import _

# starting from 0.6.0 version plone.z3cform has IWrappedForm interface
try:
    from plone.z3cform.interfaces import IWrappedForm
    HAS_WRAPPED_FORM = True
except ImportError:
    HAS_WRAPPED_FORM = False

from plone.formwidget.captcha.widget import CaptchaFieldWidget
from plone.formwidget.captcha.validator import CaptchaValidator

MSG_PORTLET_DESCRIPTION = _(
    u'This portlet shows a form to contact the corresponding agent for a '
    u'given listing via email.'
)

EMAIL_TEMPLATE = """\
Enquiry from: %(name)s <%(sender_from_address)s>
Listing URL: %(url)s

Phone Number: %(phone)s

Message:
%(message)s
"""

EMAIL_TEMPLATE_RL = """\
Enquiry from: %(name)s <%(sender_from_address)s>
Listing URL: %(url)s

Phone Number: %(phone)s
Arrival Date: %(arrival_date)s
Departure Date: %(departure_date)s
Adults: %(adults)s
Children: %(children)s

Message:
%(message)s
"""

EMAIL_TEMPLATE_ORIGINAL_AGENT = """
The responsible agent for this listing is %(agent)s (%(profile)s).

Please contact %(agent)s at %(agent_email)s.
"""


check_email = re.compile(
    r'[a-zA-Z0-9._%-]+@([a-zA-Z0-9-]+\.)*[a-zA-Z]{2,4}').match

check_for_url = re.compile(
    r'http[s]?://').search


def validate_email(value):
    if value:
        if not check_email(value):
            raise Invalid(_(u'Invalid email address'))
    return True


def contains_nuts(value):
    """Check for traces of nuts, like urls or other spammer fun things"""
    if value:
        if check_for_url(value):
            raise Invalid(_(u'No Urls allowed'))
    return True


class IEmailForm(Interface):
    """Email Form schema."""

    subject = schema.TextLine(
        required=False,
        title=PMF(u'label_subject', default=u'Subject')
    )

    name = schema.TextLine(
        description=PMF(
            u'help_sender_fullname',
            default=u'Please enter your full name',
        ),
        required=True,
        title=PMF(u'label_name', default=u"Name"),
    )

    sender_from_address = schema.TextLine(
        constraint=validate_email,
        description=PMF(
            u'help_sender_from_address',
            default=u'Please enter your e-mail address',
        ),
        required=True,
        title=PMF(u'label_sender_from_address', default=u'E-Mail'),
    )

    phone = schema.TextLine(
        description=_(
            u'Please enter a phone number. Some agents will not respond '
            u'without one.'
        ),
        missing_value=u'-',
        required=False,
        title=_(u'Phone Number'),
    )

    arrival_date = schema.TextLine(
        missing_value=u'-',
        required=False,
        title=_(u'Arrival Date'),
    )

    departure_date = schema.TextLine(
        missing_value=u'-',
        required=False,
        title=_(u'Departure Date'),
    )

    adults = schema.TextLine(
        missing_value=u'-',
        required=False,
        title=_(u'Adults'),
    )

    children = schema.TextLine(
        missing_value=u'-',
        required=False,
        title=_(u'Children'),
    )

    message = schema.Text(
        constraint=contains_nuts,
        description=PMF(
            u'help_message',
            default=u'Please enter the message you want to send.',
        ),
        max_length=1000,
        required=True,
        title=PMF(u'label_message', default=u'Message'),
    )

    captcha = schema.TextLine(
        required=True,
        title=_(u'Captcha'),
    )


class EmailForm(form.Form):
    """Email Form."""
    fields = field.Fields(IEmailForm).omit(
        'arrival_date', 'departure_date', 'adults', 'children',
    )
    ignoreContext = True
    method = 'post'
    _email_sent = False

    def __init__(self, context, request, portlet_hash=None, info=None,
                 data=None):
        super(EmailForm, self).__init__(context, request)
        self.listing_info = info
        self.data = data
        if portlet_hash:
            self.prefix = portlet_hash + '.' + self.prefix
        self.check_for_spam = data.reject_links

    @property
    def already_sent(self):
        return self._email_sent

    @property
    def is_residential_lease(self):
        return self.listing_info.get('listing_id', '').lower().startswith('rl')

    def update(self):
        if self.is_residential_lease:
            self.fields = field.Fields(IEmailForm)
        self.fields['captcha'].widgetFactory = CaptchaFieldWidget
        super(EmailForm, self).update()

    def updateWidgets(self):
        super(EmailForm, self).updateWidgets()
        urltool = getToolByName(self.context, 'portal_url')
        portal = urltool.getPortalObject()
        subject = u'%(portal_title)s: %(title)s (%(lid)s)' % dict(
            lid=self.listing_info['listing_id'],
            portal_title=portal.getProperty('title').decode('utf-8'),
            title=self.listing_info['listing_title'],
        )
        self.widgets['subject'].mode = HIDDEN_MODE
        self.widgets['subject'].value = subject

        if not self.check_for_spam:
            schema_field = copy.copy(self.widgets['message'].field)
            schema_field.constraint = lambda x: True
            self.widgets['message'].field = schema_field

    @button.buttonAndHandler(PMF(u'label_send', default='Send'), name='send')
    def handle_send(self, action):
        """Send button for sending the email."""
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        if 'captcha' in data:
            # Verify the user input against the captcha
            captcha = CaptchaValidator(
                self.context, self.request, None, IEmailForm['captcha'], None,
            )
            if not self.already_sent and captcha.validate(data['captcha']):
                self.send_email(data)
                self._email_sent = True
        return

    def send_email(self, data):
        mailhost = getToolByName(self.context, 'MailHost')
        urltool = getToolByName(self.context, 'portal_url')
        portal = urltool.getPortalObject()
        email_charset = portal.getProperty('email_charset')

        # Construct and send a message.
        from_address = portal.getProperty('email_from_address')
        from_name = portal.getProperty('email_from_name')
        if from_name is not None:
            from_address = '%s <%s>' % (from_name, from_address)

        review_recipient = getattr(self.data, 'recipient', None)
        if review_recipient is not None:
            rcp = review_recipient
        else:
            try:
                agent = self.listing_info['agent']
                rcp = agent.get('agent_email').get('value')
            except:
                rcp = from_address

        sender = '%s <%s>' % (data['name'], data['sender_from_address'])
        subject = data['subject']
        data['url'] = self.request.getURL()
        overridden = self.listing_info.get('overridden', False)
        if overridden is True or review_recipient is not None:
            orig_agent = self.listing_info.get('original_agent')
            agent_data = {
                'agent': orig_agent.get('name').get('value'),
                'agent_email': orig_agent.get('agent_email').get('value'),
                'profile': orig_agent.get('profile'),
            }
            agent = EMAIL_TEMPLATE_ORIGINAL_AGENT % agent_data
            data['message'] = '\n'.join([data['message'], agent])
        if self.is_residential_lease:
            message = EMAIL_TEMPLATE_RL % data
        else:
            message = EMAIL_TEMPLATE % data
        message = message_from_string(message.encode(email_charset))
        message['To'] = rcp
        message['From'] = from_address
        if getattr(self.data, 'bcc', None) is not None:
            message['Bcc'] = self.data.bcc
        message['Reply-to'] = sender
        message['Subject'] = subject

        mailhost.send(message, immediate=True, charset=email_charset)
        return

# Register Captcha validator for the captcha field in the ICaptchaForm
validator.WidgetValidatorDiscriminators(
    CaptchaValidator, field=IEmailForm['captcha'])


class IAgentContactPortlet(IPortletDataProvider):
    """A portlet which sends an email to the agent."""

    heading = schema.TextLine(
        description=_(
            u'Custom title for the portlet. If no title is provided, the '
            u'default title is used.'
        ),
        required=False,
        title=_(u'Portlet Title'),
    )

    description = schema.Text(
        description=_(u'Additional description for the portlet.'),
        required=False,
        title=_('Description'),
    )

    mail_sent_msg = schema.Text(
        description=_(
            u'Thank you message that is shown after the mail was sent.'
        ),
        required=False,
        title=_(u'Mail Sent Message'),
    )

    recipient = schema.TextLine(
        constraint=validate_email,
        description=_(
            u'Override the recipient e-mail address. Leave blank to use the '
            u'e-mail address from the agent information.'
        ),
        required=False,
        title=_(u'Override Recipient'),
    )

    bcc = schema.TextLine(
        description=_(
            u'E-mail addresses which receive a blind carbon copy (comma '
            u'separated).'
        ),
        required=False,
        title=_(u'BCC Recipients'),
    )

    reject_links = schema.Bool(
        default=True,
        description=_(
            u'Activate for Spam Protection. Any attempt to use a link inside '
            u'this form will raise a validation error.'
        ),
        required=False,
        title=_(u'Reject Text with Links?'),
    )


@implementer(IAgentContactPortlet)
class Assignment(base.Assignment):
    """Agent Contact Portlet Assignment."""

    heading = FieldProperty(IAgentContactPortlet['heading'])
    description = FieldProperty(IAgentContactPortlet['description'])
    mail_sent_msg = FieldProperty(IAgentContactPortlet['mail_sent_msg'])
    recipient = FieldProperty(IAgentContactPortlet['recipient'])
    bcc = FieldProperty(IAgentContactPortlet['bcc'])
    reject_links = FieldProperty(IAgentContactPortlet['reject_links'])

    title = _(u'Agent Contact')

    def __init__(self, heading=None, description=None, mail_sent_msg=None,
                 bcc=None, reject_links=None):
        self.heading = heading
        self.description = description
        self.mail_sent_msg = mail_sent_msg
        self.bcc = bcc
        self.reject_links = reject_links


class Renderer(base.Renderer):
    """Agent Information Portlet Renderer."""

    render = ViewPageTemplateFile('templates/agent_contact.pt')

    @property
    def already_sent(self):
        return self.form.already_sent

    @property
    def available(self):
        return IListingDetails.providedBy(self.view) and \
            getattr(self.view, 'listing_id', None) is not None

    @property
    def description(self):
        return self.data.description

    @property
    def mail_sent_msg(self):
        return self.data.mail_sent_msg or PMF(u'Mail sent.')

    @property
    def title(self):
        return self.data.heading or self.data.title

    def update(self):
        if self.view.info is None:
            return
        listing_info = {
            'listing_id': self.view.info.get('id').get('value'),
            'listing_title': self.view.info.get('title').get('value'),
            'agent': self.view.contact.get('agent'),
            'original_agent': self.view.contact.get('original_agent'),
            'overridden': self.view.contact.get('overridden', False),
        }

        z2.switch_on(self, request_layer=IFormLayer)
        portlet_hash = self.__portlet_metadata__.get('hash')
        self.form = EmailForm(aq_inner(self.context), self.request,
                              portlet_hash, listing_info, self.data)
        if HAS_WRAPPED_FORM:
            alsoProvides(self.form, IWrappedForm)
        self.form.update()


class AddForm(base.AddForm):
    """Add form for the Agent Contact portlet."""
    form_fields = formlib.form.Fields(IAgentContactPortlet)
    label = _(u'Add Agent Information portlet')
    description = MSG_PORTLET_DESCRIPTION

    def create(self, data):
        assignment = Assignment()
        formlib.form.applyChanges(assignment, self.form_fields, data)
        return assignment


class EditForm(base.EditForm):
    """Edit form for the Agent Contact portlet"""
    form_fields = formlib.form.Fields(IAgentContactPortlet)
    label = _(u'Edit Agent Information portlet')
    description = MSG_PORTLET_DESCRIPTION
