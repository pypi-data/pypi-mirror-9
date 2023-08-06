
Green Rocket
============

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
