# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import HttpResponseRedirect
from django.views.generic.base import TemplateView
from django.shortcuts import get_object_or_404

from .models import MailConfirmation

from .signals import confirmed as confirmed_signal


class Confirm(TemplateView):

    def user_permitted(self, request, confirmation, *args, **kwargs):
        if confirmation.forusers.exists():
            if request.user not in confirmation.forusers.all():
                return False
        return True

    def dispatch(self, request, confirmationid, *args, **kwargs):
        confirmation = get_object_or_404(MailConfirmation,
                                         confirmationid=confirmationid)
        if not self.user_permitted(request, confirmation, *args, **kwargs):
            if request.user.is_anonymous():
                return redirect_to_login(request.get_full_path(),
                                         settings.LOGIN_URL,
                                         REDIRECT_FIELD_NAME)
            else:
                raise PermissionDenied

        with transaction.atomic():
            if not confirmation.confirmed:
                confirmation.confirmed = True
                confirmation.save()
                confirmed_signal.send(
                    sender=MailConfirmation,
                    toconfirm_type=confirmation.toconfirm_object.__class__,
                    object_id=confirmation.toconfirm_object.id)

            self.template_name = confirmation.confirm_success_template or confirmation.toconfirm_object._meta.app_label + '/mail_confirmation_succeeded.html'

            if confirmation.confirm_success_url:
                return HttpResponseRedirect(confirmation.confirm_success_url)

            return self.render_to_response({
                'confirmation': confirmation})
