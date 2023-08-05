# -*- coding: utf8 -*-
import unittest
from pysmsru import SMSRU


API_ID = 'fc65780b-8c69-a164-1519-6343b9e365fb'


class TestSendSms(unittest.TestCase):
    def setUp(self):
        pass

    def test_send_one(self):
        smsru = SMSRU(
            api_id='fc65780b-8c69-a164-1519-6343b9e365fb',
            debug=True,
            sendername='lukyoung',
        )
        smsru.send_one(phone_to='79214050080', message='test')


if __name__ == '__main__':
    unittest.main()
