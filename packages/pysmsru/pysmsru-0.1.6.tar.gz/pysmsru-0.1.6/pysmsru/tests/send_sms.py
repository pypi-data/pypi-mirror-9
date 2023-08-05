# -*- coding: utf8 -*-
import unittest
from pysmsru import SMSRU


class TestSendSms(unittest.TestCase):
    def setUp(self):
        pass

    def Xtest_send_one_wrong_sender_name(self):
        smsru = SMSRU(
            debug=True,
            sendername='lukyoung',
        )
        smsru.send_one(phone_to='79214050080', message='test')

    def test_send_one(self):
        smsru = SMSRU(
            debug=True
        )
        smsru.send_one(phone_to='79214050080', message='test')


if __name__ == '__main__':
    unittest.main()
