"""SMTP email backend class."""
try:
    import pickle
except ImportError:# pragma: no cover
    import cPickle as pickle
import logging
from threading import RLock as threading_RLock
from datetime import datetime, timedelta
from copy import copy
from queue_front import queues
from django.core.mail.backends.smtp import EmailBackend
from mailqueue_backend import settings

def reload_settings():
    ''' used for unit testing '''
    try:
        from imp import reload
    except ImportError:# pragma: no cover
        pass
    reload(settings)

LFH = logging.handlers.RotatingFileHandler(settings.LOG_FILENAME,
    maxBytes=settings.LOG_FILE_MAXBYTES,
    backupCount=settings.LOG_FILE_BACKUP)
LFH.setLevel(logging.WARNING)
FORMATTER = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - '
    '%(message)s')
LFH.setFormatter(FORMATTER)
LOGGER = logging.getLogger('smtp.mail_queue')
LOGGER.addHandler(LFH)

class QueuedEmailBackend(EmailBackend):
    """
    A wrapper that manages the SMTP network connection.
    """
    SENT = (True, None)
    NOQUEUE = (False, False)
    DOQUEUE = (False, True)
    @staticmethod
    def _wrap(email, created=None, **kwargs):
        '''make and pickle the data'''
        data = {
            'email':email,
            'created':datetime.now() if created == None else created
        }
        data.update(kwargs)
        return pickle.dumps(data)

    @staticmethod
    def _make_pickleable(obj):
        """
            Make the email message picklable. Email messages have reference to
            the class
        """
        obj_copy = copy(obj)
        if hasattr(obj_copy, 'connection'):
            obj_copy.connection = None
        return obj_copy

    def __init__(self, host=None, port=None, username=None, password=None,
                 use_tls=None, fail_silently=False, test=False, **kwargs):
        super(QueuedEmailBackend, self).__init__(host=host, port=port,
            username=username, password=password, use_tls=use_tls,
            fail_silently=fail_silently, test=test, **kwargs)
        if test:
            reload_settings()
        self.que = queues.Queue(settings.QUEUE_NAME)
        self._lock2 = threading_RLock()

    def send_messages(self, email_messages, **kwargs):
        """
        Store messages in queue
        """
        self._store(email_messages, **kwargs)
        return len(email_messages)

    def _store(self, email_messages, **kwargs):
        """
        Do the actual storing
        """
        for email_message in email_messages:
            self.que.write(self._wrap(self._make_pickleable(email_message),
                **kwargs))

    def _send_queued_messages(self, email_message, expired, email_message_dict):
        """
        Check or set any extra metadata here in a subclass using
        email_message_dict

        returns whether or not the message should be requeued or discarded.
        """
        try:
            fail = super(QueuedEmailBackend, self).send_messages(
                [email_message]) == 0
        except Exception as err:
            fail = True
        if fail:
            created = email_message_dict.get('created')
            if created < expired:# if message has expired do not requeue it
                LOGGER.warning('Message Expired. Created:{0}, Subject: {3}, '
                    'From:{1}, To:{2}.'.format(
                    created,
                    email_message.from_email,
                    ', '.join(email_message.to),
                    email_message.subject
                ))
                return self.NOQUEUE # not sent, do not queue
            return self.DOQUEUE# not sent, do queue
        return self.SENT # sent

    def send_queued_messages(self, expire=None):
        """
        Send the queued messages
        """
        with self._lock2:
            expire = settings.QUEUE_EXPIRE if expire is None else expire
            expired = datetime.now() - timedelta(seconds=expire)
            wasdiscarded = 0
            length = sent = len(self.que)
            for i in range(length):
                email_message_dict = pickle.loads(self.que.read())
                email_message = email_message_dict.pop('email')
                wassent, doqueue = self._send_queued_messages(email_message,
                    expired, email_message_dict)
                if not wassent:
                    sent -= 1
                    if doqueue:
                        self.que.write(self._wrap(email_message,
                            **email_message_dict))
                    else:
                        wasdiscarded += 1
        return (sent, wasdiscarded, length)
