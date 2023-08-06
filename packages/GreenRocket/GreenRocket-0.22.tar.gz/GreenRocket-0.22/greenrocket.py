"""
Green Rocket is a simple and compact implementation of Observer
(or Publish/Subscribe) design pattern via signals.

Create specific signal using base one:

..  code-block:: pycon

    >>> from greenrocket import Signal
    >>> class MySignal(Signal):
    ...     pass
    ...

Subscribe handler:

..  code-block:: pycon

    >>> @MySignal.subscribe
    ... def handler(signal):
    ...     print('handler: ' + repr(signal))
    ...

Fire signal:

..  code-block:: pycon

    >>> MySignal().fire()
    handler: MySignal()

Note, that signal propagates over inheritance, i.e. all subscribers of base
signal will be called when child one is fired:

..  code-block:: pycon

    >>> @Signal.subscribe
    ... def base_handler(signal):
    ...     print('base_handler: ' + repr(signal))
    ...
    >>> MySignal().fire()
    handler: MySignal()
    base_handler: MySignal()

Unsubscribe handler:

..  code-block:: pycon

    >>> MySignal.unsubscribe(handler)
    >>> MySignal().fire()
    base_handler: MySignal()

The handler is subscribed using weak reference.  So if you create and subscribe
a handler in local scope (for example inside a generator), it will be
unsubscribed automatically.

..  code-block:: pycon

    >>> def gen():
    ...     @MySignal.subscribe
    ...     def local_handler(signal):
    ...         print('local_handler: ' + repr(signal))
    ...     yield 1
    ...
    >>> for value in gen():
    ...     MySignal(value=value).fire()
    ...
    local_handler: MySignal(value=1)
    base_handler: MySignal(value=1)
    >>> import gc                    # PyPy fails the following test without
    >>> _ = gc.collect()             # explicit call of garbage collector.
    >>> MySignal(value=2).fire()
    base_handler: MySignal(value=2)
    >>> Signal.unsubscribe(base_handler)

As you can see above, signal constructor accepts keyword arguments.  These
arguments are available as signal's attributes:

..  code-block:: pycon

    >>> s = MySignal(a=1, b=2)
    >>> s.a
    1
    >>> s.b
    2

Signal suppresses any exception which is raised on handler call.  It uses
logger named ``greenrocket`` from standard ``logging`` module to log errors and
debug information.

The library also provides ``Watchman`` class as a convenient way for testing
signals.

Create watchman for specific signal:

..  code-block:: pycon

    >>> from greenrocket import Watchman
    >>> watchman = Watchman(MySignal)

Fire signal:

..  code-block:: pycon

    >>> MySignal(x=1).fire()

Test signal:

..  code-block:: pycon

    >>> watchman.assert_fired_with(x=1)
    >>> watchman.assert_fired_with(x=2)          # DOCTEST: +ellipsis
    Traceback (most recent call last):
      ...
    AssertionError: Failed assertion on MySignal.x: 1 != 2
    >>> watchman.assert_fired_with(x=1, y=2)     # DOCTEST: +ellipsis
    Traceback (most recent call last):
      ...
    AssertionError: MySignal has no attribute y

Watchman object saves each fired signal to its log:

..  code-block:: pycon

    >>> watchman.log
    [MySignal(x=1)]
    >>> MySignal(x=2).fire()
    >>> watchman.log
    [MySignal(x=1), MySignal(x=2)]

The method ``assert_fired_with`` tests the last signal from
the log by default:

..  code-block:: pycon

    >>> watchman.assert_fired_with(x=2)

But you can specify which one to test:

..  code-block:: pycon

    >>> watchman.assert_fired_with(-2, x=1)

"""

from logging import getLogger
try:
    from weakref import WeakSet
except ImportError:                         # pragma: nocover
    # Python 2.6
    from weakrefset import WeakSet          # pragma: nocover


__all__ = ['Signal', 'Watchman']
__version__ = '0.22'
__author__ = 'Dmitry Vakhrushev <self@kr41.net>'
__license__ = 'BSD'


class SignalMeta(type):
    """ Signal Meta Class """

    def __init__(cls, class_name, bases, attrs):
        cls.__handlers__ = WeakSet()


# For compatibility between Python 2.x and Python 3.x
BaseSignal = SignalMeta('BaseSignal', (object,), {})


class Signal(BaseSignal):
    """ Base Signal Class """

    logger = getLogger(__name__)

    @classmethod
    def subscribe(cls, handler):
        """ Subscribe handler to signal.  May be used as decorator """
        cls.logger.debug('Subscribe %r on %r', handler, cls)
        cls.__handlers__.add(handler)
        return handler

    @classmethod
    def unsubscribe(cls, handler):
        """ Unsubscribe handler from signal """
        cls.logger.debug('Unsubscribe %r from %r', handler, cls)
        cls.__handlers__.discard(handler)

    def __init__(self, **kw):
        self.__dict__.update(kw)

    def __repr__(self):
        params = []
        for k, v in self.__dict__.items():
            params.append('{0}={1!r}'.format(k, v))
        params = ', '.join(params)
        return '{0}({1})'.format(self.__class__.__name__, params)

    def fire(self):
        """ Fire signal """
        self.logger.debug('Fired %r', self)
        for cls in self.__class__.__mro__:
            if hasattr(cls, '__handlers__'):
                self.logger.debug('Propagate on %r', cls)
                for handler in cls.__handlers__:
                    try:
                        self.logger.debug('Call %r', handler)
                        handler(self)
                    except:
                        self.logger.error('Failed on processing %r by %r',
                                          self, handler, exc_info=True)


class Watchman(object):

    def __init__(self, signal_class):
        self.log = []
        self.signal_name = signal_class.__name__
        signal_class.subscribe(self)

    def __call__(self, signal):
        self.log.append(signal)

    def assert_fired_with(self, index=-1, **kw):
        try:
            signal = self.log[index]
        except IndexError:
            raise AssertionError(
                'There is no {signal} in the log at index {index}'.format(
                    signal=self.signal_name,
                    index=index,
                )
            )
        for attr, expected in kw.items():
            if not hasattr(signal, attr):
                raise AssertionError(
                    '{signal} has no attribute {attr}'.format(
                        signal=self.signal_name,
                        attr=attr,
                    )
                )
            actual = getattr(signal, attr)
            if actual != expected:
                raise AssertionError(
                    'Failed assertion on {signal}.{attr}: '
                    '{actual!r} != {expected!r}'.format(
                        signal=self.signal_name,
                        attr=attr,
                        actual=actual,
                        expected=expected,
                    )
                )
