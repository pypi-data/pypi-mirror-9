import os

SITE_ID = 1
SITE_SCHEME = 'https'
SITE_DOMAIN = 'example.com'
DATABASE_ENGINE = 'sqlite3'

ROOT_URLCONF = 'mail_confirmation.tests.urls'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

INSTALLED_APPS = [
    'django.contrib.sites',
    'django.contrib.contenttypes',
    'mail_confirmation',
    'mail_confirmation.tests',
]

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

# This is only needed for the 1.4.X test environment
USE_TZ = True

SECRET_KEY = 'easy'
