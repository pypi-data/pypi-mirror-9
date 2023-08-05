#Installation

You must have setuptools installed.

From PyPI:

    pip install django_mailqueue_backend

Or download a package from the [PyPI][PyPI Page] or the [BitBucket page][Bit Page]:

    pip install <package>

Or unpack the package and:

    python setup.py install.

[PyPI Page]: https://pypi.python.org/pypi/django_mailqueue_backend
[Bit Page]: https://bitbucket.org/dwaiter/django-mailqueue-backend/downloads

##Dependencies

Django >=1.4,<1.5,>=1.6 and its dependencies.

queue-front >= 0.7.2 located at: [https://bitbucket.org/dwaiter/queue-front/][bitbucket queue] or
[https://pypi.python.org/pypi/queue-front][pypi queue].
Note that queue-front also has dependencies. See [this page][bitbucket queue] for more details.

[bitbucket queue]: https://bitbucket.org/dwaiter/queue-front/
[pypi queue]: https://pypi.python.org/pypi/queue-front


##Integration
In your Django settings.py file insert the following in an appropriate place:

    ...

    INSTALLED_APPS = [
        ...
        "mailqueue_backend",
        ...
    ]

    ...

    EMAIL_BACKEND = "mailqueue_backend.mail.smtp.QueuedEmailBackend"
    ...

That is it. You should run the following command by any regular means that you prefer
(cron, celery, etc):

    ./manage.py process_mail_queue

#Mail Storage

Mail is stored in a queue. The backend for the queue is specified by you
in the queue-front app.

#Compatibility

This module has been tested with the following:
(Note that python 3.0 compatibility is dependent on the backend queue you choose
to use with the queue-front dependency.)

* python 2.7 django 1.4
* python 2.7 django 1.6
* python 2.7 django 1.7
* python 3.2 django 1.6
* python 3.2 django 1.7
* python 3.3 django 1.6
* python 3.3 django 1.7
* python 3.4 django 1.6
* python 3.4 django 1.7

#Advanced

##Packages Security

This module, when packaged, is signed with the following key:

Mario Rosa's Key with id 0x8EBBFA6F (full fingerprint F261 96E4 8EF2 ED4A 26F8  58E9 04AA
48D1 8EBB FA6F) and his email is mario@dwaiter.com

You can find this key on servers like [pgp.mit.edu][PGP MIT].

[PGP MIT]: http://pgp.mit.edu

##Additional Settings

###MAIL\_QUEUE\_NAME
Default: "MAIL_QUEUE"

Set the name of the queue.

###MAIL\_QUEUE\_LOG\_FILENAME
Default: "smtp.mail\_queue.mail\_queue\_fail.log"

A log to this file will be made when a message is discarded.

###MAIL\_QUEUE\_LOG\_FILE\_MAXBYTES
Default: 5242880 (Integer) aka 5MB

Maximum size of a log file.

###MAIL\_QUEUE\_LOG\_FILE\_BACKUP
Default: 5 (Integer)

Number (n) of files in log rotation. A new backup is created once MAXBYTES is
reached in the current log file up to n many log files. The oldest log file
is deleted on rotation (i.e. n+1).

###MAIL\_QUEUE\_EXPIRE
Default: 86400 (Integer) aka 1 day

The amount of time in seconds until a failed email is discarded from the queue.
