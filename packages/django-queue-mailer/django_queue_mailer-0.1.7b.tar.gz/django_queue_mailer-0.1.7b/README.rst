Django Queue Mailer
===================

A reusable Django app for controlling queuing and sending of app emails.
Key use case is to move sending of emails out of requests to speed-up
request time and help to solve problems with sending email, handling
deferring of email and logging of app email communication.

App started as a fork of Derek Stegelman's `Django Mail
Queue <https://github.com/dstegelman/django-mail-queue>`__ and heavilly
inspired by James Tauber's
`django-mailer <https://github.com/pinax/django-mailer>`__.

Any feedback, issues and suggestions are welcome. In that case please
use `Bitbucket's
issues <https://bitbucket.org/edke/django-queue-mailer/issues>`__.

Key features
------------

-  Emails are queued and send as asynchronous task with help of Celery
   or Huey or as a crontab job scheduler.
-  With use of own backend easily integrated into existing app.
-  Easily configurable to use different mail backends as Django's SMTP
   backend or Amazon SES using `Sea
   Cucumber <https://github.com/duointeractive/sea-cucumber>`__.

Installation
------------

Install django\_queue\_mailer:

::

    $ pip install django_queue_mailer

Add the following to your settings.py:

::

    # Add django_queue_mailer to INSTALLED_APPS
    INSTALLED_APPS = (
        ...
        "django_queue_mailer",
        ...
    )

    # Add django_queue_mailer's backend
    EMAIL_BACKEND = "django_queue_mailer.backend.DbBackend"

    # Setup email backend for sending queued emails
    DJANGO_QUEUE_MAILER_EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

    # Or other backed as Sea Cucumber
    DJANGO_QUEUE_MAILER_EMAIL_BACKEND = "seacucumber.backend.SESBackend"

You need to create the necessary tables. If you use
`south <https://bitbucket.org/andrewgodwin/south/>`__, just run
migrations:

::

    $ python manage.py migrate django_queue_mailer

If not, normal ``syncdb`` will do. For easier package upgrades using
`south <https://bitbucket.org/andrewgodwin/south/>`__ for database
migrations is strongly recommended.

::

    $ python manage.py syncdb

Basic usage
-----------

Send emails and put them in queue with Django's send\_mail function:

::

    from django.core.mail import send_mail

    send_mail('Subject here', 'Here is the message.', 'from@example.com',
        ['to@example.com'], fail_silently=False)

Alternatively you can queue message with use of Queue model:

::

    from django_queue_mailer.models import Queue

    new_message = Queue()
    new_message.subject = "Testing subject"
    new_message.to_address = "nobody@example.com, noone@example.com"
    new_message.bcc_address = "blindcopy@example.com"
    new_message.from_address = "hello@example.com"
    new_message.content = "Mail content"
    new_message.html_content = "<h1>Mail Content</h1>"
    new_message.app = "someapp"
    new_message.save()

Queued messages can be send with use of
`Celery <https://github.com/celery/django-celery/>`__ as asynchronous
tasks. Example of Celery task, tasks.py in your app folder:

::

    from django_queue_mailer.models import Queue

    @celery.task
    def send_mail():
        Queue.objects.send_queued()

`Huey <https://github.com/coleifer/huey>`__ is a perfect lightweight
Celery alternative. Example of using it's multi-threaded tasks,
periodical or event based (called from request when needed). Configure
task in tasks.py:

::

    from huey.djhuey import task, periodic_task, crontab
    from django.core.management import call_command

    @task()
    @periodic_task(crontab(minute='*/2'))
    def send_mail():
        call_command('send_queued_messages')

Simplest solution is to run crontab job, configure crontab using
``crontab -e``:

::

    */2 * * * * path-to-virtualenv/bin/python path-to-app-folder/manage.py send_queued_messages

Further documentation
---------------------

Will be added.
