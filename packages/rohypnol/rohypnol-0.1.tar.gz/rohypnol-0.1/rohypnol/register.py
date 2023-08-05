from django.conf import settings
from django.db.models.base import ModelBase
from django.db.models.signals import post_save
from django.dispatch import Signal
from django.core.cache import cache


class RohypnolRegister(object):

    def __init__(self):
        # The _registry is a dictionary like:
        # {
        #     signal0: {
        #         model0: set(['key0']),
        #         model1: set(['key0','key1'])
        #     },
        #     signal1: {
        #         model0: set(['key2']),
        #         model2: set(['key0','key2'])
        #     },
        # }
        self._registry = {}

    def register(self, models, keys, signals=post_save, **kwargs):
        """Registers a combination of one or more models, one or more keys and
        one or more signals.

        Whenever one of the signals is sent by one of the models, the
        associated cache keys will be deleted.

        By default, if you omit the `signals` parameter it will use the Django
        `post_save` signal.

        Example usage:

        from rohypnol.register import rohypnol

        # This will issue a cache.delete('article_list') whenever an article
        # is saved
        rohypnol.register(Article, 'article_list')

        # Like the one above, but it will work for the custom signal instead
        # of `post_save`
        custom_signal = Signal()
        rohypnol.register(Article, 'article_list', custom_signal)

        # Combining things
        rohypnol.register(Article, 'article_list', (post_save, custom_signal))

        # Even more
        rohypnol.register(Article, 
                          ('article_list', 'top_articles'),
                          (post_save, custom_signal))

        # Finally
        rohypnol.register((Article, Category), 
                          ('article_list', 'top_articles'),
                          (post_save, custom_signal))
        """
        if not isinstance(signals, (list, tuple)):
            signals = [signals]
        for signal in signals:
            if settings.DEBUG:
                err = "%s is not a valid Signal subclass." % signal
                assert isinstance(signal, Signal), err
            self._registry.setdefault(signal, {})
            if not isinstance(models, (list, tuple)):
                models = [models]
            for model in models:
                if settings.DEBUG:
                    err = "%s is not a valid ModelBase subclass." % model
                    assert isinstance(model, ModelBase), err
                self._registry.get(signal).setdefault(model, set())
                if not isinstance(keys, (list, tuple)):
                    keys = [keys]
                for key in keys:
                    self._registry.get(signal).get(model).add(key)

    def connect(self):
        """
        Connects all current registered signals to the cache delete function.
        """
        for signal, models in self._registry.iteritems():
            for model, keys in models.iteritems():
                # Local function the current signal is going to be
                # connected to.
                # Defining it dynamically allows us to pass in the current
                # set of keys for the given model, but we have to store
                # a strong reference to it to avoid garbage collection.
                def delete_cache(signal, sender=model, keys=keys):
                    cache.delete_many(list(keys))
                signal.connect(delete_cache, sender=model, weak=False, dispatch_uid=signal)

    def disconnect(self):
        """
        Disconnects all current registered signals.
        To reconnect, signals must be registered again.
        """
        for signal, models in self._registry.iteritems():
            for model, keys in models.iteritems():
                signal.disconnect(sender=model, weak=False, dispatch_uid=signal)
        self._registry = {}

rohypnol = RohypnolRegister()

def connect_all_signals():
    """Connects all registered signals.

    This code should live in your url.py file in order to be executed once,
    when all your applications are loaded.
    """
    rohypnol.connect()
