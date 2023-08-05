# -*- encoding: utf-8 -*-


import unittest

from dateconv import *


class TestAll(unittest.TestCase):
    def test_times(self):
        human_time = '2015-01-01 18:21:26'
        datetime_time = datetime.datetime(2015, 1, 1, 18, 21, 26)
        my_unix_time = 1420136486  # GMT
        # my_unix_time = 1420114886  # local

        self.assertEqual(d2u(datetime_time), my_unix_time)
        self.assertEqual(d2h(datetime_time), human_time)
        self.assertEqual(h2u(human_time), my_unix_time)
        self.assertEqual(h2d(human_time), datetime_time)
        self.assertEqual(u2d(my_unix_time), datetime_time)
        self.assertEqual(u2h(my_unix_time), human_time)

    def test_exeptions(self):
        self.assertRaises(DateConvException, d2h, (123, ))
        self.assertRaises(DateConvException, d2h, ('fds', ))

        try:
            d2h(datetime.datetime.now())
        except DateConvException:
            self.fail("raised Exception unexpectedly!")


if __name__ == '__main__':
    unittest.main()
