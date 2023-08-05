"""
sigdispatch
~~~~~~~~~~~

Sigdispatch is a simple events library.

    >>> import sigdispatch
    >>> def on_foo(payload):
    ...     print('Received %s.' % payload)
    ...
    >>> def another_on_foo(payload):
    ...     print('Received %s too.' % payload)
    ...
    >>> sigdispatch.observe('foo', on_foo) #doctest: +ELLIPSIS
    <function ...>
    >>> sigdispatch.observe('foo', another_on_foo) #doctest: +ELLIPSIS
    <function ...>
    >>> sigdispatch.emit('foo', [1, 2, 3]) #doctest: +ELLIPSIS
    Received ...
    Received ...

This library implements a signal dispatcher between components of your
application, so that they can send messages (signals) to each other
in a decoupled fashion; emitters don't know which components are receiving
their signals.

See :py:class:`SignalDispatcher` for details of the intrinsics.

.. data:: default_dispatcher

   An instance of :py:class:`SignalDispatcher`. Calls to
   :py:func:`sigdispatch.observe`, :py:func:`emit` and
   :py:func:`on_exceptions` are method invocations of this object.

.. automodule:: sigdispatch.signal_dispatcher
   :members:
"""

__version__ = '0.0.1'


class SignalDispatcher(object):
    """
    A **signal dispatcher** is a channel for sending signals through. It makes
    signals arrive to its observers (ie. dispatches them).

    A **signal** is an arbitrary message which can be emitted and received.

    A signal has a **code**, a string that identifies which kind of signal it
    is.

    A signal also may have a **payload**; it can be any value, provided it's
    JSON-seralizable by the standard ``json.JSONEncoder``.

    A **signal dispatch** is the process of emitting a signal and waiting for
    every observer on the signal's code to be called. A signal dispatch, thus,
    is *synchronous*; the execution of the emitter will be resumed once the
    execution of all those observers finish.

    A ``SignalDispatcher`` instance provides :py:meth:`SignalDispatcher.emit`
    for emitting signals, and :py:meth:`SignalDispatcher.observe` for
    registering callbacks for getting notified when signals of a specific code
    are emitted (that's called **observing on** a signal code).

    All **exceptions** raised in a dispatch by the observers will be caught, so
    they won't stop other observers from being called. As the signal emitter
    shouldn't know about the observers, nor about the exceptions they may
    raise, they aren't raised again. Instead, a callback for when exceptions
    happen can be registered with :py:meth:`SignalDispatcher.on_exceptions`.
    """

    def __init__(self):
        self._observers = {}
        self._exception_handlers = []

    def observe(self, code, observer):
        """
        Declares an observer function for a signal code.

        When a signal is emitted with the given code and a payload,
        ``observer`` will be called with that payload as argument.

        Args:
            code (str): A signal code to observe on.
            observer (callable): A function that takes a payload.

        Returns:
            A function that, when called, unsets the observer, so that it will
            no longer be called when signals of that code are dispatched.
        """
        _assert_is('code', str, code)
        _assert_is_callable('observer', observer)

        if not code in self._observers:
            self._observers[code] = {observer}
        else:
            self._observers[code].add(observer)

        def unobserve():
            self._observers[code].remove(observer)

        return unobserve

    def emit(self, code, payload=None):
        """
        Emits a signal with the given code.

        Observers of that signal code will be called with the given payload as
        argument.

        Args:
            code (str): A signal code whose observers call.
            payload: An arbitrary value. It will be passed to each observer
                of the emitted signal.
        """
        _assert_is('code', str, code)

        observers = self._observers.get(code, None)
        if not observers:
            return

        exceptions = self._emit_to_observers(code, payload, observers)

        self._handle_exceptions(code, payload, exceptions)

    def on_exceptions(self, callback):
        """
        Sets a handler for all exceptions caught in a dispatch.

        All exceptions that were raised during a dispatch will be put together
        in a list. The callback function will be called with the signal code,
        the payload and the list of exceptions.

        Additional calls will set additional callbacks.

        Args:
            callback (callable): A function that takes a code (str), an
                arbitrary payload value, and a list of exceptions.
        """
        _assert_is_callable('callback', callback)

        self._exception_handlers.append(callback)

    def _emit_to_observers(self, code, payload, observers):
        exceptions = []

        for observer in observers:
            try:
                observer(payload)
            except Exception as e:
                exceptions.append(e)

        return exceptions

    def _handle_exceptions(self, code, payload, exceptions):
        if not self._exception_handlers or not exceptions:
            return

        for handler in self._exception_handlers:
            try:
                handler(code, payload, exceptions)
            except:
                pass


def _assert_is(name, type_, val):
    assert isinstance(val, type_), "%s is not a %s: %r" % (name, val)


def _assert_is_callable(name, val):
    assert callable(val), "%s is not callable: %r" % (name, val)


default_dispatcher = SignalDispatcher()


def observe(*args, **kwargs):
    """
    Calls ``default_dispatcher.observe``.
    See :py:meth:`.SignalDispatcher.observe`.
    """
    return default_dispatcher.observe(*args, **kwargs)


def emit(*args, **kwargs):
    """
    Calls ``default_dispatcher.emit``.
    See :py:meth:`.SignalDispatcher.emit`.
    """
    return default_dispatcher.emit(*args, **kwargs)


def on_exceptions(*args, **kwargs):
    """
    Calls ``default_dispatcher.observe``.
    See :py:meth:`.SignalDispatcher.on_exceptions`.
    """
    return default_dispatcher.on_exceptions(*args, **kwargs)
