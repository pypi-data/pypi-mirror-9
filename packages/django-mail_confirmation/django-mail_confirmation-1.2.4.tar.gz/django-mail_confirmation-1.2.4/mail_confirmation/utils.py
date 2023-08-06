# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from django.utils import six
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext as _
from django.template.loader import render_to_string
from django.conf import settings
from django.core.urlresolvers import reverse

from datetime import datetime, timedelta
import logging
import collections

logger = logging.getLogger(__name__)

from .models import MailConfirmation


def get_users(to):
    if not isinstance(to, collections.Iterable):
        to = (to,)
    else:
        to = set(to)
    return filter(lambda x: isinstance(x, get_user_model()), to)


def generate_confirmation(toconfirm,
                          success_template='',
                          success_url='',
                          confirmed=False,
                          forusers=(),
                          *args, **kwargs):
    """
    Generates a confirmation email object
    """
    try:
        confirm = MailConfirmation(
            toconfirm_object=toconfirm,
            confirm_success_url=success_url,
            confirm_success_template=success_template,
            confirmed=confirmed)

        confirm.save()
        users = get_users(forusers)
        if users:
            confirm.forusers.add(*users)
    except Exception, e:
        logger.error('Could not generate confirmation for mail_confirmation: '+str(e)) # noqa
        raise
    return confirm



def send_confirmation(confirm, request_template=None,
                      subject=_('Confirmation mail'),
                      sender=None,
                      to=(),
                      confirmurlname='mail_confirmation:url',
                      context=None,
                      *args, **kwargs):
    """
    Send a confirmation mail
    """

    if sender is None:
        sender = settings.DEFAULT_FROM_EMAIL
    if isinstance(to, six.string_types):
        to = [to]
    try:
        scheme = settings.MAIL_CONFIRMATION_SCHEME
    except:
        scheme = 'https'
    try:
        from django.contrib.sites.models import Site
        domain = Site.objects.get_current().domain
    except:
        domain = settings.SITE_DOMAIN or ""

    url = reverse(confirmurlname,
                  kwargs={'confirmationid': confirm.confirmationid})
    request_template = request_template or confirm.toconfirm_object._meta.app_label + '/mail_request.html' # noqa
    basecontext = {'confirmation_url': url,
                   'SITE_SCHEME': scheme,
                   'SITE_DOMAIN': domain}
    if context:
        basecontext.update(context)
    message = render_to_string(request_template, basecontext)
    return send_mail(subject, message, sender,
                     to, fail_silently=False)


def generate_and_send(toconfirm,
                      request_template=None,
                      success_template='',
                      success_url='',
                      forusers=(),
                      mail_function=None,
                      *args,
                      **kwargs):
    """
    Do both actions above
    """
    confirm = generate_confirmation(toconfirm,
                                    success_template, success_url,
                                    forusers=forusers,
                                    *args, **kwargs)
    if confirm:
        if mail_function:
            return mail_function(confirm,
                                 request_template,
                                 forusers=forusers,
                                 *args, **kwargs)
        else:
            return send_confirmation(confirm,
                                     request_template,
                                     forusers=forusers,
                                     *args, **kwargs)
    return confirm


def clear_stale():
    """
    Clears stale requests not confirmed
    """
    try:
        delta = settings.MAIL_CONFIRMATION_STALE_PERIOD
    except:
        delta = 30
    if delta:
        last_month = datetime.today() - timedelta(days=30)
        MailConfirmation.objects.filter(date_created__lte=last_month).delete()
