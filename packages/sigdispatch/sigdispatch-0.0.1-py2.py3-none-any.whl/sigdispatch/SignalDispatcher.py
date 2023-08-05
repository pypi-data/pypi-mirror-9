class SignalDispatcher(object):
    """
    Hey.
    """

    def __init__(self):
        self._observers = {}
        self._exception_handlers = []

    def observe(self, code, observer):
        """
        Test.
        """
        _assert_is('code', str, code)
        _assert_is_callable('observer', observer)

        if not code in self._observers:
            self._observers[code] = [observer]
        else:
            self._observers[code].append(observer)

    def emit(self, code, payload=None):
        _assert_is('code', str, code)

        if not code in self._observers:
            return

        observers = self._observers.get(code, None)
        if not observers:
            return

        exceptions = self._emit_to_observers(code, payload, observers)

        self._handle_exceptions(code, payload, exceptions)

    def on_exceptions(self, callback):
        _assert_is_callable('callback', callback)

        self._exception_handler = callback

    def _emit_to_observers(self, code, payload, observers):
        exceptions = []

        for observer in observers:
            try:
                observer(payload)
            except Exception as e:
                exceptions.push(e)

        return exceptions

    def _handle_exception(self, code, payload, exceptions):
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
