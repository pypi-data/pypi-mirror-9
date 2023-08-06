"""
Copyed from https://github.com/SmileyChris/easy-thumbnails/blob/d6c5f3f8ae7a830b49ebb87fdda4b0b1d0bbf916/easy_thumbnails/migrations/__init__.py

Django migrations for mail_confirmation app
This package does not contain South migrations. South migrations can be found
in the ``south_migrations`` package.
"""
SOUTH_ERROR_MESSAGE = """\n
For South support, customize the SOUTH_MIGRATION_MODULES setting like so:
SOUTH_MIGRATION_MODULES = {
'mail_confirmation': 'mail_confirmation.south_migrations',
}
"""
# Ensure the user is not using Django 1.6 or below with South
try:
    from django.db import migrations # noqa
except ImportError:
    from django.core.exceptions import ImproperlyConfigured
    raise ImproperlyConfigured(SOUTH_ERROR_MESSAGE)
