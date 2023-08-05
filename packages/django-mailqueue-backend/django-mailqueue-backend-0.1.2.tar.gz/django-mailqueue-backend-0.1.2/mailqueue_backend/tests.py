''' Run tests of the package '''
import sys
try:
    import cStringIO as io
except ImportError:# pragma: no cover
    import io
from django.test import TestCase
from django.test.utils import override_settings
from django.core.mail import EmailMultiAlternatives
from django.core.management import call_command
from queue_front import queues

def capture(func, *args, **kwargs):
    """Capture the output of func when called with the given arguments.

    The function output includes any exception raised. capture returns
    a tuple of (function result, standard output, standard error).
    """
    stdout, stderr = sys.stdout, sys.stderr
    sys.stdout = str1 = io.StringIO()
    sys.stderr = str2 = io.StringIO()
    result = func(*args, **kwargs)
    sys.stdout = stdout
    sys.stderr = stderr
    return (result, str1.getvalue(), str2.getvalue())

SUBJECT, FROM_EMAIL, TO = 'hello', 'from@example.com', 'to@example.com'
TEXT_CONTENT = 'This is an important message.'
HTML_CONTENT = '<p>This is an <strong>important</strong> message.</p>'
QUEUE_NAME = 'TEST_QUEUE'
EMAIL_BACKEND = "mailqueue_backend.mail.smtp.QueuedEmailBackend"

@override_settings(MAIL_QUEUE_NAME=QUEUE_NAME, EMAIL_BACKEND=EMAIL_BACKEND)
class SendMailTest(TestCase):
    '''The test suite'''
    def setUp(self):
        '''setup the queue and empty it'''
        self.que = queues.Queue(QUEUE_NAME)
        for i in range(len(self.que)):# pragma: no cover
            self.que.read()

    @staticmethod
    def send_message():
        '''send a message'''
        msg = EmailMultiAlternatives(SUBJECT, TEXT_CONTENT,
            FROM_EMAIL, [TO])
        msg.attach_alternative(HTML_CONTENT, "text/html")
        msg.send()

    @override_settings(EMAIL_HOST='', MAIL_QUEUE_EXPIRE=86400)
    def test_re_queue(self):
        ''' message will be requeued after fail '''
        self.send_message()
        self.assertEqual(len(self.que), 1)
        capture(call_command, 'process_mail_queue', 'test')
        self.assertEqual(len(self.que), 1)
        self.que.read()

    @override_settings(EMAIL_HOST='', MAIL_QUEUE_EXPIRE=0)
    def test_de_queue(self):
        ''' message will expire and be dequeued '''
        self.send_message()
        self.assertEqual(len(self.que), 1)
        capture(call_command, 'process_mail_queue', 'test')
        self.assertEqual(len(self.que), 0)

    def test_send(self):
        ''' send message '''
        self.send_message()
        self.assertEqual(len(self.que), 1)
        capture(call_command, 'process_mail_queue', 'test')
        self.assertEqual(len(self.que), 0)
