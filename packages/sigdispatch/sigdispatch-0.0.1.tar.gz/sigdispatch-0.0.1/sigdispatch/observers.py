"""
sigdispatch.observers
~~~~~~~~~~~~~~~~~~~~~

Helpers for using :py:mod:`sigdispatch` in a conventional style.

    >>> from sigdispatch.observers import Observer
    >>> class BuzzwordsObserver(Observer):
    ...     def on_holistic(self, payload):
    ...         print('A holistic approach to %s.' % payload)
    ...
    ...     def on_proactive(self, payload):
    ...         print("We're looking for passionate, proactive %s to join us." % payload)
    ...
    >>> o = BuzzwordsObserver()
    >>> o.register()
    >>> sigdispatch.emit('holistic', 'social media influence content viral impact')
    A holistic approach to social media influence content viral impact.
    >>> sigdispatch.emit('proactive', 'keyboard banger')
    We're looking for passionate, proactive keyboard banger to join us.

"""
from abc import ABCMeta
import sigdispatch


class BaseObserver(object):
    """
    An abstract class that establishes a convention for observing
    :py:class:`sigdispatch.SignalDispatcher` s in a uniform, cohesive, nice
    style.

    Children classes should implement observer methods for a number of
    signal codes. They are supposed to be related in functionality, perhaps
    sharing some state between signal dispatches.
    """
    __metaclass__ = ABCMeta

    def __init__(self):
        self._dispatcher = None
        self._unobservers = []

    def register(self, dispatcher=sigdispatch.default_dispatcher):
        """
        Starts observing signals in a signal dispatcher.

        Every method on ``self`` with a name like ``on_some_signal_code`` will
        aftwerwards be called with a payload whenever a ``some_signal_code``
        signal is emitted.

        Args:
            dispatcher (sigdispatch.SignalDispatcher): The signal dispatcher
                from which the methods will observe. It defaults to
                :py:data:`sigdispatch.default_dispatcher`.

        Raises:
            AlreadyRegisteredException: When called more than once with no
                py:meth:``unregister`` in between.
        """
        if self._dispatcher:
            raise AlreadyRegisteredException(self)

        for attr_name in dir(self):
            attr_value = getattr(self, attr_name)
            if not callable(attr_value):
                continue
            if not attr_name.startswith('on_'):
                continue
            undo = dispatcher.observe(attr_name[3:], attr_value)
            self._unobservers.append(undo)

        self._dispatcher = dispatcher

    def unregister(self):
        """
        Stops ``self`` from observing signals.

        Calling it when ``self`` is not registered does nothing.
        """
        if not self._dispatcher:
            return

        for u in self._unobservers:
            u()

        self._dispatcher = None


class Observer(BaseObserver):
    """
    A default-featured, no-brainer :py:class:`BaseObserver`. It just inherits
    from the :py:class:`BaseObserver` children that are supposed to be default
    functionality. Users of this library should probably inherit their
    observers from this class.
    """
    __metaclass__ = ABCMeta


class AlreadyRegisteredException(Exception):
    """
    Raised when attempting to register a :py:class:`BaseObserver` in a signal
    dispatcher when it was already registered.
    """

    def __init__(self, obj):
        super(AlreadyRegisteredException, self).__init__(
            'observer object %r already registered in signal dispatcher.' %
            obj
        )
