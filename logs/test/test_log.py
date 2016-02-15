from unittest import TestCase
from sw_utils.logs.log_handler import log_info, rootLogger, log_trace
from django.conf import settings


class TestLog(TestCase):
    def tearDown(self):
        pass

    def setUp(self):
        setattr(settings, 'DB_NAME', 'localhost')
        setattr(settings, 'DB_USER', '')
        setattr(settings, 'DB_PASS', '')

    def test_log_anything(self):
        e1 = BaseException("aa")
        e2 = BaseException("bb")
        log_info(e1)
        log_info(e1)
        log_info("a")
        log_info("%s", "b")
        log_info(e1)
        log_info("%s", e1)

        def fun(a):
            1 / 0

        try:
            fun(1)
        except BaseException as e:
            log_info(e)

    def test_new_log_levels(self):

        rootLogger.setLevel(level=16)
        log_trace('una trace at level 6 no se deberia mostar')

        rootLogger.setLevel(level=15)
        log_trace('una trace at level 5 debe mostarse')

    def test_levels(self):
        pass
