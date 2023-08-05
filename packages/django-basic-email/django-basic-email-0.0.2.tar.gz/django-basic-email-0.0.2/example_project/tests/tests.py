# -*- coding: utf-8 -*-
from django.test import TestCase
from django.core import mail

from basic_email.send import send_email


class EmailsTests(TestCase):

    def test_send(self):
        send_email('start', 'foo@bar.com', 'Lorem')
        self.assertEqual(len(mail.outbox), 1)
