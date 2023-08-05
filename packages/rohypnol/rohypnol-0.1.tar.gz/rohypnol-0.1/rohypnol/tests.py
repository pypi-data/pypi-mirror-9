from django.utils import unittest
from django.test.utils import override_settings
from django.db import models
from django.dispatch import Signal
from django.core.cache import cache

from rohypnol.register import RohypnolRegister, rohypnol, connect_all_signals

mock_signal_0 = Signal()
mock_signal_1 = Signal()

class MockModelA(models.Model): pass
class MockModelB(models.Model): pass

class RegisterTest(unittest.TestCase):

    def test_register(self):
        r = RohypnolRegister()
        
        r.register(MockModelA, 'k0', mock_signal_0)
        self.assertEqual(r._registry, {
            mock_signal_0: {MockModelA: set(['k0'])}
        })

        r.register(MockModelA, 'k0', mock_signal_1)
        self.assertEqual(r._registry, {
            mock_signal_0: {MockModelA: set(['k0'])},
            mock_signal_1: {MockModelA: set(['k0'])}
        })

        r.register(MockModelA, 'k0', (mock_signal_0, mock_signal_1))
        self.assertEqual(r._registry, {
            mock_signal_0: {MockModelA: set(['k0'])},
            mock_signal_1: {MockModelA: set(['k0'])}
        })

        r.register(MockModelA, 'k1', (mock_signal_0, mock_signal_1))
        self.assertEqual(r._registry, {
            mock_signal_0: {MockModelA: set(['k0', 'k1'])},
            mock_signal_1: {MockModelA: set(['k0', 'k1'])},
        })

        r.register(MockModelA, ('k0', 'k2'), mock_signal_0)
        self.assertEqual(r._registry, {
            mock_signal_0: {MockModelA: set(['k0', 'k1', 'k2'])},
            mock_signal_1: {MockModelA: set(['k0', 'k1'])},
        })

        r.register(MockModelB, ('k0', 'k2'), mock_signal_0)
        self.assertEqual(r._registry, {
            mock_signal_0: {MockModelA: set(['k0', 'k1', 'k2']), MockModelB: set(['k0', 'k2'])},
            mock_signal_1: {MockModelA: set(['k0', 'k1'])},
        })

        r.register((MockModelA, MockModelB), ('k0', 'k2'), (mock_signal_0, mock_signal_1))
        self.assertEqual(r._registry, {
            mock_signal_0: {MockModelA: set(['k0', 'k1', 'k2']), MockModelB: set(['k0', 'k2'])},
            mock_signal_1: {MockModelA: set(['k0', 'k1', 'k2']), MockModelB: set(['k0', 'k2'])},
        })

    @override_settings(DEBUG=True)
    def test_wrong_signal(self):
        r = RohypnolRegister()
        self.assertRaises(AssertionError, r.register, MockModelA, 'k0', 'mock_signal_0')

    @override_settings(DEBUG=True)
    def test_wrong_model(self):
        r = RohypnolRegister()
        self.assertRaises(AssertionError, r.register, 'MockModelA', 'k0', mock_signal_0)

    def test_delete(self):
        k0, k1, k2 = 'k0', 'k1', 'k2'
        v0, v1, v2 = 'v0', 'v1', 'v2'
        cache_timeout = 10
        r = RohypnolRegister()

        def set_cache():
            cache.set(k0, v0, cache_timeout)
            cache.set(k1, v1, cache_timeout)
            cache.set(k2, v2, cache_timeout)
            r.disconnect()

        set_cache()
        r.register(MockModelA, k0, mock_signal_0)
        r.register(MockModelB, k1, mock_signal_1)
        r.connect()
        mock_signal_0.send(sender=MockModelA)
        self.assertIsNone(cache.get(k0))
        self.assertIsNotNone(cache.get(k1))
        self.assertIsNotNone(cache.get(k2))
        mock_signal_1.send(sender=MockModelB)
        self.assertIsNone(cache.get(k0))
        self.assertIsNone(cache.get(k1))
        self.assertIsNotNone(cache.get(k2))
        mock_signal_0.send(sender=MockModelB)
        self.assertIsNone(cache.get(k0))
        self.assertIsNone(cache.get(k1))
        self.assertIsNotNone(cache.get(k2))

        set_cache()
        r.register(MockModelA, k0, (mock_signal_0, mock_signal_1))
        r.connect()
        mock_signal_0.send(sender=MockModelA)
        self.assertIsNone(cache.get(k0))
        self.assertIsNotNone(cache.get(k1))
        self.assertIsNotNone(cache.get(k2))
        mock_signal_1.send(sender=MockModelA)
        self.assertIsNone(cache.get(k0))
        self.assertIsNotNone(cache.get(k1))
        self.assertIsNotNone(cache.get(k2))
        mock_signal_0.send(sender=MockModelB)
        self.assertIsNone(cache.get(k0))
        self.assertIsNotNone(cache.get(k1))
        self.assertIsNotNone(cache.get(k2))
        mock_signal_1.send(sender=MockModelB)
        self.assertIsNone(cache.get(k0))
        self.assertIsNotNone(cache.get(k1))
        self.assertIsNotNone(cache.get(k2))

        set_cache()
        r.register((MockModelA, MockModelB), (k0, k1), mock_signal_0)
        r.connect()
        mock_signal_0.send(sender=MockModelA)
        self.assertIsNone(cache.get(k0))
        self.assertIsNone(cache.get(k1))
        self.assertIsNotNone(cache.get(k2))
        mock_signal_0.send(sender=MockModelB)
        self.assertIsNone(cache.get(k0))
        self.assertIsNone(cache.get(k1))
        self.assertIsNotNone(cache.get(k2))
        mock_signal_1.send(sender=MockModelA)
        self.assertIsNone(cache.get(k0))
        self.assertIsNone(cache.get(k1))
        self.assertIsNotNone(cache.get(k2))

        set_cache()
        r.register((MockModelA, MockModelB), k0, (mock_signal_0, mock_signal_1))
        r.connect()
        mock_signal_0.send(sender=MockModelA)
        self.assertIsNone(cache.get(k0))
        self.assertIsNotNone(cache.get(k1))
        self.assertIsNotNone(cache.get(k2))
        mock_signal_1.send(sender=MockModelA)
        self.assertIsNone(cache.get(k0))
        self.assertIsNotNone(cache.get(k1))
        self.assertIsNotNone(cache.get(k2))
        mock_signal_0.send(sender=MockModelB)
        self.assertIsNone(cache.get(k0))
        self.assertIsNotNone(cache.get(k1))
        self.assertIsNotNone(cache.get(k2))
        mock_signal_1.send(sender=MockModelB)
        self.assertIsNone(cache.get(k0))
        self.assertIsNotNone(cache.get(k1))
        self.assertIsNotNone(cache.get(k2))

        set_cache()
        r.register(MockModelA, (k0, k1), mock_signal_0)
        r.register(MockModelB, (k0, k2), mock_signal_0)
        r.connect()
        mock_signal_1.send(sender=MockModelA)
        self.assertIsNotNone(cache.get(k0))
        self.assertIsNotNone(cache.get(k1))
        self.assertIsNotNone(cache.get(k2))
        mock_signal_0.send(sender=MockModelA)
        self.assertIsNone(cache.get(k0))
        self.assertIsNone(cache.get(k1))
        self.assertIsNotNone(cache.get(k2))
        mock_signal_0.send(sender=MockModelB)
        self.assertIsNone(cache.get(k0))
        self.assertIsNone(cache.get(k1))
        self.assertIsNone(cache.get(k2))

        set_cache()
        r.register(MockModelA, (k0, k1), mock_signal_0)
        r.register(MockModelB, (k0, k2), mock_signal_1)
        r.connect()
        mock_signal_0.send(sender=MockModelB)
        self.assertIsNotNone(cache.get(k0))
        self.assertIsNotNone(cache.get(k1))
        self.assertIsNotNone(cache.get(k2))
        mock_signal_1.send(sender=MockModelA)
        self.assertIsNotNone(cache.get(k0))
        self.assertIsNotNone(cache.get(k1))
        self.assertIsNotNone(cache.get(k2))
        mock_signal_1.send(sender=MockModelB)
        self.assertIsNone(cache.get(k0))
        self.assertIsNotNone(cache.get(k1))
        self.assertIsNone(cache.get(k2))

        set_cache()
        r.register(MockModelA, k0, mock_signal_0)
        r.register(MockModelA, k1, mock_signal_0)
        r.register(MockModelA, k2, mock_signal_0)
        r.connect()
        mock_signal_0.send(sender=MockModelA)
        self.assertIsNone(cache.get(k0))
        self.assertIsNone(cache.get(k1))
        self.assertIsNone(cache.get(k2))

        set_cache()
        r.register(MockModelA, k0, mock_signal_0)
        r.register(MockModelA, k1, mock_signal_0)
        r.register(MockModelA, k2, mock_signal_0)
        r.connect()
        mock_signal_0.send(sender=MockModelA)
        self.assertIsNone(cache.get(k0))
        self.assertIsNone(cache.get(k1))
        self.assertIsNone(cache.get(k2))

        set_cache()
        r.register(MockModelA, k0, mock_signal_1)
        r.register(MockModelA, k1, mock_signal_0)
        r.register(MockModelA, k2, mock_signal_0)
        r.connect()
        mock_signal_0.send(sender=MockModelA)
        self.assertIsNotNone(cache.get(k0))
        self.assertIsNone(cache.get(k1))
        self.assertIsNone(cache.get(k2))
        mock_signal_0.send(sender=MockModelB)
        self.assertIsNotNone(cache.get(k0))
        self.assertIsNone(cache.get(k1))
        self.assertIsNone(cache.get(k2))

    def test_connect_all_signals(self):
        k0, k1, k2 = 'k0', 'k1', 'k2'
        v0, v1, v2 = 'v0', 'v1', 'v2'
        cache_timeout = 10

        def set_cache():
            cache.set(k0, v0, cache_timeout)
            cache.set(k1, v1, cache_timeout)
            cache.set(k2, v2, cache_timeout)
            rohypnol.disconnect()

        set_cache()
        rohypnol.register(MockModelA, k0, mock_signal_0)
        rohypnol.register(MockModelB, k1, mock_signal_1)
        connect_all_signals()
        mock_signal_0.send(sender=MockModelA)
        self.assertIsNone(cache.get(k0))
        self.assertIsNotNone(cache.get(k1))
        self.assertIsNotNone(cache.get(k2))
        mock_signal_1.send(sender=MockModelB)
        self.assertIsNone(cache.get(k0))
        self.assertIsNone(cache.get(k1))
        self.assertIsNotNone(cache.get(k2))
        mock_signal_0.send(sender=MockModelB)
        self.assertIsNone(cache.get(k0))
        self.assertIsNone(cache.get(k1))
        self.assertIsNotNone(cache.get(k2))