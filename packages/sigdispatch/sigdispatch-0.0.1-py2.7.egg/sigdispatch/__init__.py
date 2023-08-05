"""
sigdispatch
~~~~~~~~~~~

Sigdispatch is a simple events library.

>>> import sigdispatch
>>> def on_foo(payload):
...     print 'Received %s' % payload
...
>>> sigdispatch.observe('foo', on_foo)
>>> sigdispatch.emit('foo', 'bar')
Received bar

.. data:: default_dispatcher

   An instance of :py:class:`SignalDispatcher`. Calls to
   :py:func:`sigdispatch.observe`, :py:func:`emit` and
   :py:func:`on_exceptions` are method invocations of this object.

.. automodule:: sigdispatch.SignalDispatcher
   :members:
"""

__version__ = '0.0.1'

from .SignalDispatcher import SignalDispatcher


default_dispatcher = SignalDispatcher()


def observe(*args, **kwargs):
    """
    Calls ``default_dispatcher.observe``.
    See :py:meth:`.SignalDispatcher.observe`.
    """
    default_dispatcher.observe(*args, **kwargs)


def emit(*args, **kwargs):
    """
    Calls ``default_dispatcher.emit``.
    See :py:meth:`.SignalDispatcher.emit`.
    """
    default_dispatcher.emit(*args, **kwargs)


def on_exceptions(*args, **kwargs):
    """
    Calls ``default_dispatcher.observe``.
    See :py:meth:`.SignalDispatcher.on_exceptions`.
    """
    default_dispatcher.on_exceptions(*args, **kwargs)
