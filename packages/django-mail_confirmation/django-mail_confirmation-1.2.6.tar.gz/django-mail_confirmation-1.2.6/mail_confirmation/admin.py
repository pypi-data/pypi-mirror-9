# coding=utf-8
from django.contrib import admin

from .models import MailConfirmation

def confirmation_id(obj):
    return ("%s" % (obj.confirmationid)).upper()


class MCAdmin(admin.ModelAdmin):
    list_display = (confirmation_id, 'confirmed', 'date_created', 'toconfirm_type', 'toconfirm_object')

admin.site.register(MailConfirmation, MCAdmin)
