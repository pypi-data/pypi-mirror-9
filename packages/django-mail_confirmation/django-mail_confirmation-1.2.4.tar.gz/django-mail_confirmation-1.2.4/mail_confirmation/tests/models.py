# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.contenttypes import generic
from django.core.mail import mail_admins

from ..models import MailConfirmation
from ..signals import confirmed as confirmed_signal

class Confirmed(models.Model):
    confirmed = generic.GenericRelation(
        MailConfirmation,
        content_type_field='toconfirm_type',
        object_id_field='toconfirm_id')

    @classmethod
    def application_confirmed_callback(cls, sender, toconfirm_type, object_id, **kwargs):
        if toconfirm_type == cls:
            url = ''.join(['http://example.com/confirmed/', str(object_id)])
            body = "check the website for that new application " + url
            mail_admins("New model application", body)


confirmed_signal.connect(Confirmed.application_confirmed_callback,
                         sender=MailConfirmation)
