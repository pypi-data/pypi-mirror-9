HOW IT WORKS
============

mail_confirmation is a general application for approving a certain object in your application via user mail confirmation, that is:
you create an object, tell mail_confirmation to generate and send a mail confirmation to the user, and the user clicking a link in the email he receives confirms your object.

INSTALLATION
============


put this in your urls.

::

    from mail_confirmation.views import MailConfirmation

    #Mail url Confirmation
    urlpatterns += patterns('',
                              url(r'^confirm/', include('mail_confirmation.urls', namespace='mail_confirmation')),
    )

and mail_confirmation in your installed apps settings

::

    INSTALLED_APPS += (
        'mail_confirmation',
    )

and then run syncdb

In the model that you want confirmations put a generic relation field to easy lookup approvations

::

    from django.contrib.contenttypes import generic
    from mail_confirmation.models import MailConfirmation

    confirmed = generic.GenericRelation(MailConfirmation,
                                       content_type_field='toconfirm_type',
                                       object_id_field='toconfirm_id')
    
With this you could see confirmed object filtering by myobj.confirmed = True

(Nota bene: you could do this, and not using the actual field myobj.confirmed.confirmed , because the models returns that field as part of his representation,

note also that in the orm you must check for confirmed__confirmed=True)

You **must** also provide a template in `youapplication/mail_request.html` that will be used as email body and a template in  `yourapplication/mail_confirmation_succeded.html` that will display a thank you message for the user, you could override their names, see below.

Read below on how to connect to a signal emitted whenever a model is confirmed by the user

SETTINGS
========

settings.MAIL_CONFIRMATION_SCHEME  defaults to http

settings.MAIL_CONFIRMATION_STALE_PERIOD period after deletion of stale requests

settings.DEFAULT_FROM_EMAIL if no email is provided as sender use this one

USAGE
=====

Note, you can look up tests/test.py to see an example of usage, see `MailConfirmationTest.test_confirmation` how uses the relevant object to confirm and how it is made from `tests.models`

Creating your object
--------------------
say you have a model MyModel with a `confirmed` field of the kind explained above, you create it
  
::

    obj = MyModel()

and ask `mail_confirmation` to send a confirmation email to the user.


Sending confirmations to the user
---------------------------------

to send a confirmation you put this snippet in your code.

::

    from mail_confirmation.utils import generate_and_send

    generate_and_send(obj,
                      mailtemplate, 
                      success_template, success_url,
                      subject, sender, to)

obj in an instance of a model that needs a confirmation from the user.
mailtemplate is a template name used by render_to_string(template)
and there is passed a key `url` , that you need to display in the email body as link confirmation.
Success_template is the template shown by the default success view, otherwise if you specify success_url that view redirects to a view of yours,  after triggering signal and updating the model.

specifically the message will be rendered by

::

    message = render_to_string(mailtemplate, {'url': url})

**Default values:**

mailtemplate: `yourapplication/templates/yourapplication/mail_request.html`

subject: `"Confirmation mail"`

success_url: None

success_template: `yourapplication/templates/yourapplication/mail_confirmation_succeded.html`,

sender: `settings.DEFAULT_FROM_EMAIL`



look at utils for scomposed functions that divide the generation
and sending logic if you need them deferred

you can configure the url name used by reverse to compose the confirmation url
by passing urlname='name' to send_confirmation or generate_and_send


Getting the confirmed id
------------------------

Whenever a confirmation is made from an user a signal is emitted
you can connect to that signal and do things™ with this code:

::

    from mail_confirmation.signals import confirmed_signal

    confirmed_signal.connect(my_callback)

or

::

    @receiver(confirmed_signal, 
              sender=MailConfirmation)
    def my_callback(sender, toconfirm_type, object_id, **kwargs):
        if toconfirm_type == MyModel:
            print("do something")

where toconfirm_type is the model you passed as instance to the confirmation generation
and object_id is the id of your MyModel object


Clearing stale requests
-----------------------

import from utils clear_stale() or a celery task that runs every first of the month is provided for you.

::

    CELERY_IMPORTS += (
        'mail_confirmation.tasks',
    ) 


you also should set  settings.MAIL_CONFIRMATION_STALE_PERIOD to a timedelta in days

it defaults to 30 days, set it to 0 to disable temporarly

TESTS
=====

./manage.py test mail_confirmation --settings=mail_confirmation.tests.settings

