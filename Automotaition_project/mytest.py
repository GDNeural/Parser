import unittest
from mail_sender import *


class MyFirstTests(unittest.TestCase):

    def test_mail_send(self):
        self.assertEqual(
            Email.send_message('dovgopolovis@cash-u.com', 'Илья', 'dovgopolovis@cash-u.com', '12345Qwerty!'),
            'Message sent successfully')