from Products.CMFCore.utils import getToolByName
from collective.registrationcaptcha.interfaces import IBrowserLayer
from plone.app.discussion.browser.validator import CaptchaValidator
from plone.app.discussion.interfaces import ICaptcha
from plone.app.discussion.interfaces import IDiscussionSettings
from plone.app.users.browser.register import RegistrationForm
from plone.protect import CheckAuthenticator
from plone.registry.interfaces import IRegistry
from plone.z3cform.fieldsets import extensible
from z3c.form import interfaces
from z3c.form.field import Fields
from zope.component import adapts
from zope.component import queryUtility
from zope.interface import Interface


class NonExistentException(Exception):
    """Dummy exception for usage instead of exceptions from missing plugins.
    """

try:
    from plone.app.discussion.browser.validator import WrongNorobotsAnswer
except ImportError:
    WrongNorobotsAnswer = NonExistentException

try:
    from plone.app.discussion.browser.validator import WrongCaptchaCode
except ImportError:
    WrongCaptchaCode = NonExistentException


class CaptchaRegistrationForm(RegistrationForm):
    """RegistrationForm with captcha functionality.
    """

    def validate_registration(self, action, data):

        # CSRF protection
        CheckAuthenticator(self.request)

        # Validate Captcha
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings, check=False)
        portal_membership = getToolByName(self.context, 'portal_membership')
        captcha_enabled = settings.captcha != 'disabled'
        anon = portal_membership.isAnonymousUser()
        if captcha_enabled and anon:
            if 'captcha' not in data:
                data['captcha'] = u""
            try:
                captcha = CaptchaValidator(self.context,
                                           self.request,
                                           None,
                                           ICaptcha['captcha'],
                                           None)
                captcha.validate(data['captcha'])
            except (WrongCaptchaCode, WrongNorobotsAnswer):
                # Error messages are fed in by the captcha widget itself.
                pass

        del data['captcha']  # delete, so that value isn't stored
        super(CaptchaRegistrationForm,
              self).validate_registration(action, data)


class CaptchaRegistrationFormExtender(extensible.FormExtender):
    """Registrationform extender to extend it with the captcha schema.
    """
    adapts(Interface, IBrowserLayer, CaptchaRegistrationForm)
    fields = Fields(ICaptcha)

    def __init__(self, context, request, form):
        self.context = context
        self.request = request
        self.form = form

        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings, check=False)
        self.captcha = settings.captcha
        portal_membership = getToolByName(self.context, 'portal_membership')
        self.isAnon = portal_membership.isAnonymousUser()

    def update(self):
        if self.captcha != 'disabled' and self.isAnon:
            # Add a captcha field if captcha is enabled in the registry
            self.add(ICaptcha, prefix="")
            if self.captcha == 'captcha':
                from plone.formwidget.captcha import CaptchaFieldWidget
                self.form.fields['captcha'].widgetFactory = CaptchaFieldWidget
            elif self.captcha == 'recaptcha':
                from plone.formwidget.recaptcha import ReCaptchaFieldWidget
                self.form.fields['captcha'].widgetFactory = \
                    ReCaptchaFieldWidget
            elif self.captcha == 'norobots':
                from collective.z3cform.norobots import NorobotsFieldWidget
                self.form.fields['captcha'].widgetFactory = NorobotsFieldWidget
            else:
                self.form.fields['captcha'].mode = interfaces.HIDDEN_MODE
