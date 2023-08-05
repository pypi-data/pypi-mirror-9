# -*- coding: utf-8 -*-
import re

from django.core import mail
from django.test import TestCase
from django.template import Template
from django.core.urlresolvers import reverse
from django.conf import settings

from ..utils import generate_and_send, generate_confirmation
from ..models import MailConfirmation
from .models import Confirmed

class MailConfirmationTest(TestCase):
    r = re.compile('(' + settings.SITE_SCHEME + '://' + settings.SITE_DOMAIN + '/.*)')

    def test_confirmed(self):
        obj = Confirmed()
        obj.save()
        confirm = generate_confirmation(obj, confirmed=True)
        self.assertEqual(confirm.confirmed, True)

    def test_defaults(self):
        obj = Confirmed()
        obj.save()
        t = 'confirm.html'
        ct = 'confirmed.html'

        ret = generate_and_send(obj, to='user@example.com')
        self.assertNotIn(ret, [None])
        self.assertEqual(len(mail.outbox)>=1, True)
        confirm_url = self.r.findall(mail.outbox[-1].body)[0]
        email = mail.outbox[-1]
        self.assertEqual(email.to[0], 'user@example.com')
        self.assertEqual(email.body, u'confirm ' + settings.SITE_SCHEME + '://' + settings.SITE_DOMAIN + reverse('mail_confirmation:url', kwargs={'confirmationid': obj.confirmed.all()[0].confirmationid})+ '\n')
        self.assertEqual(email.from_email, 'webmaster@localhost')
        self.assertEqual(email.subject, 'Confirmation mail')
        response = self.client.get(confirm_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0], 'tests/mail_confirmation_succeeded.html')

    def test_confirmation(self):
        """
        Tests a confirmation with a user model
        """
        obj = Confirmed()
        obj.save()

        self.assertEqual(Confirmed.objects.filter(confirmed__confirmed=True).exists(), False)

        t = 'confirm.html'
        ct = 'confirmed.html'

        generate_and_send(obj, t, ct,
                          "/success", "confirm",
                          "info@example.com", "client@example.com" )

        self.assertEqual(len(mail.outbox)>=1, True)
        confirm_url = self.r.findall(mail.outbox[-1].body)[0]

        response = self.client.get(confirm_url)

        self.assertEqual(mail.outbox[0].from_email, 'info@example.com')
        self.assertEqual(mail.outbox[0].to[0], 'client@example.com')

        self.assertEqual(MailConfirmation.objects.all()[0].confirmed, True)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(u'confirm at this url ' + confirm_url, u'confirm at this url ' + settings.SITE_SCHEME + '://' + settings.SITE_DOMAIN + reverse('mail_confirmation:url', kwargs={'confirmationid': obj.confirmed.all()[0].confirmationid}))
        self.assertEqual(Confirmed.objects.filter(confirmed__confirmed=True).exists(), True)
