import time
import random
import concert.config
from concert.devices.dummy import DummyDevice
from concert.async import async, wait, resolve, KillException, HAVE_GEVENT
from concert.tests import TestCase, VisitChecker


@async
def func():
    pass


@async
def bad_func():
    raise RuntimeError


@async
def identity(x):
    return x, x**2


class TestAsync(TestCase):

    def setUp(self):
        super(TestAsync, self).setUp()
        self.device = DummyDevice()

    def test_wait(self):
        @async
        def long_func():
            time.sleep(random.random() / 50.)

        futs = []
        for i in range(10):
            futs.append(long_func())

        wait(futs)

        for future in futs:
            self.assertTrue(future.done(), "Not all futures finished.")

    def test_exceptions(self):
        with self.assertRaises(TypeError):
            func(0).join()

        with self.assertRaises(RuntimeError):
            bad_func().join()

    def test_kill(self):
        d = {'killed': False}

        @async
        def long_op(d):
            try:
                time.sleep(1)
            except KillException:
                d['killed'] = True

        future = long_op(d)
        time.sleep(0)
        future.kill()

        if HAVE_GEVENT and concert.config.ENABLE_GEVENT:
            self.assertTrue(d['killed'])

    def test_resolve(self):
        result = (identity(x) for x in xrange(10))
        tuples = list(zip(*resolve(result)))
        self.assertEqual(len(tuples), 2)
        self.assertSequenceEqual(tuples[0], range(10))
        self.assertSequenceEqual(tuples[1], [x**2 for x in range(10)])

    def test_cancel_operation(self):
        @async
        def long_op():
            time.sleep(0.01)

        check = VisitChecker()

        f = long_op()
        f.cancel_operation = check.visit
        f.cancel()
        self.assertTrue(check.visited)
