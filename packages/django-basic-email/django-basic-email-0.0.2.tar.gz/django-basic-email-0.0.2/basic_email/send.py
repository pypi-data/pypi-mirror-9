# -*- coding: utf-8 -*-
import logging
import cssutils

from django.contrib.sites.models import Site
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings

from premailer import Premailer

cssutils.log.setLevel(logging.CRITICAL)


def send_email(template, to, subject, variables={}, fail_silently=False,
               replace_variables={}, reply_to=False, attachments=None,
               memory_attachments=None):
    variables['site'] = Site.objects.get_current()
    variables['STATIC_URL'] = settings.STATIC_URL
    variables['is_secure'] = getattr(settings, 'IS_SECURE', False)
    html = render_to_string('emails/email_%s.html' % template, variables)
    protocol = 'https://' if variables['is_secure'] else 'http://'
    replace_variables['protocol'] = protocol
    domain = variables['site'].domain
    replace_variables['domain'] = domain
    for key, value in replace_variables.items():
        if not value:
            value = ''
        html = html.replace('{%s}' % key.upper(), value)
    # Update path to have domains
    base = protocol + domain
    html = Premailer(html,
                     remove_classes=False,
                     exclude_pseudoclasses=False,
                     keep_style_tags=True,
                     include_star_selectors=True,
                     strip_important=False,
                     base_url=base).transform()
    headers = {}
    if reply_to:
        headers['Reply-To'] = reply_to
    email = EmailMessage(subject, html, settings.DEFAULT_FROM_EMAIL, [to],
                         headers=headers)
    email.content_subtype = "html"
    if attachments:
        for attachment in attachments:
            email.attach_file(attachment)
    if memory_attachments:
        for attachment in memory_attachments:
            email.attach(attachment['name'], attachment['content'],
                         attachment['mime'])
    email.send(fail_silently=fail_silently)
