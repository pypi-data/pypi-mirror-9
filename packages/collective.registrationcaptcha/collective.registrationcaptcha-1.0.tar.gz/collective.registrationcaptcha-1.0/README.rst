collective.registrationcaptcha
==============================

Add a captcha field to the @@register form for anonymous users form to secure
it from spam bots.

It depends on ``plone.app.discussion`` and uses it's captcha abstaction
facilities.

In order to use a captcha widget, you have to install one - wether
by depending on the ``captchawidgets`` extra of this package or by installing
``plone.formwidget.captcha``, ``plone.formwidget.recaptcha`` (not functional at
time of this writing) or ``collective.z3cform.norobots``.
Then you have to configure plone.app.discussion to use a captcha widget. You
don't need to keep the discussion activated, if you don't want them to be
active on your site.
