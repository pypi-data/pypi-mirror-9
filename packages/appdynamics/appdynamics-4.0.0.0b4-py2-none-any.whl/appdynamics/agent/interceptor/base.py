import sys
from functools import wraps
from contextlib import contextmanager

from appdynamics.agent.core.correlation import make_header


NOTHING = object()


class BaseInterceptor(object):
    def __init__(self, agent, cls):
        self.agent = agent
        self.cls = cls

    @property
    def bt(self):
        return self.agent.get_active_bt()

    def __setitem__(self, key, value):
        if self.bt:
            self.bt._properties[key] = value

    def __getitem__(self, key):
        if self.bt:
            return self.bt._properties.get(key)

    def __delitem__(self, key):
        if self.bt:
            self.bt._properties.pop(key, None)

    def _fix_dunder_method_name(self, method, class_name):
        # If `method` starts with '__', then it will have been renamed by the lexer to '_SomeClass__some_method'
        # (unless the method name ends with '__').
        if method.startswith('__') and not method.endswith('__'):
            method = '_' + class_name + method
        return method

    def _attach(self, method, wrapper_func, patched_method_name):
        patched_method_name = patched_method_name or '_' + method

        # Deal with reserved identifiers.
        # https://docs.python.org/2/reference/lexical_analysis.html#reserved-classes-of-identifiers
        method = self._fix_dunder_method_name(method, self.cls.__name__)
        patched_method_name = self._fix_dunder_method_name(patched_method_name, self.__class__.__name__)

        # Wrap the orignal method if required.
        original_method = getattr(self.cls, method)
        if wrapper_func:
            @wraps(original_method)
            def wrapped_method(*args, **kwargs):
                return wrapper_func(original_method, *args, **kwargs)
            real_method = wrapped_method
        else:
            real_method = original_method

        # Replace `self.cls.method` with a call to the patched method.
        patched_method = getattr(self, patched_method_name)

        @wraps(original_method)
        def call_patched_method(*args, **kwargs):
            return patched_method(real_method, *args, **kwargs)

        setattr(self.cls, method, call_patched_method)

    def attach(self, method_or_methods, wrapper_func=None, patched_method_name=None):
        if not isinstance(method_or_methods, list):
            method_or_methods = [method_or_methods]
        for method in method_or_methods:
            self._attach(method, wrapper_func, patched_method_name)

    def log_exception(self, level=1):
        self.agent.logger.exception('Exception in {klass}.{function}.'.format(
            klass=self.__class__.__name__, function=sys._getframe(level).f_code.co_name))

    @contextmanager
    def log_exceptions(self):
        try:
            yield
        except:
            self.log_exception(level=3)

    @contextmanager
    def call_and_reraise_on_exception(self, func, ignored_exceptions=()):
        try:
            yield
        except ignored_exceptions:
            raise
        except Exception as exc:
            with self.log_exceptions():
                func(exc)
            raise


class EntryPointInterceptor(BaseInterceptor):
    def attach(self, method_or_methods, patched_method_name=None):
        super(EntryPointInterceptor, self).attach(method_or_methods, wrapper_func=self.run,
                                                  patched_method_name=patched_method_name)

    def start_transaction(self, *args, **kwargs):
        """Start a new transaction.

        Note: The implementation in `agent.start_transaction` means that nothing bad happens if we try to start the same
        transaction more than once.

        """
        with self.log_exceptions():
            self.agent.start_transaction(*args, **kwargs)

    def run(self, func, *args, **kwargs):
        """Run the function.  If it raises an exception, end the transaction and re-raise the error.

        """
        with self.call_and_reraise_on_exception(self.end_transaction):
            return func(*args, **kwargs)

    def end_transaction(self, exc=None):
        """End the transaction.

        Note: The implementation in `agent.end_transaction` means that nothing bad happens if we try to end the same
        transaction more than once.

        """
        with self.log_exceptions():
            self.agent.end_transaction(exc)


class ExitCallInterceptor(BaseInterceptor):
    def attach(self, method_or_methods, wrapper_func=NOTHING, patched_method_name=None):
        # Doing it like this allows None to be a valid value for wrapper_func.
        if wrapper_func is NOTHING:
            wrapper_func = self.run
        super(ExitCallInterceptor, self).attach(method_or_methods, wrapper_func=wrapper_func,
                                                patched_method_name=patched_method_name)

    @property
    def exit_call(self):
        if self.bt:
            return self.bt._active_exit_call

    def get_backend(self):
        raise NotImplementedError('You need to implement your own `get_backend` method.')

    def add_header(self, header):
        pass

    def create_correlation_header(self):
        pass

    def add_notxdetect_header(self):
        if self.bt:
            self.add_header(make_header(self.agent, None, None))

    def start_exit_call(self, operation=None):
        """Create the exit call and add the correlation header.

        If there is no active BT, add a notxdetect header to stop a BT being created by any downstream agents.

        """
        with self.log_exceptions():
            bt = self.bt
            if bt:
                exit_call = bt.start_exit_call(sys._getframe(2), self.get_backend(), operation=operation)
                if exit_call is not None:
                    correlation_header = self.create_correlation_header()
                    if correlation_header is not None:
                        self.add_header(correlation_header)
                        exit_call.backend.optional_properties['CorrelationHeader'] = correlation_header[1]

    def run(self, func, *args, **kwargs):
        """Run the function.  If it raises an exception, end the exit call and re-raise the exception.

        """
        with self.call_and_reraise_on_exception(self.end_exit_call):
            return func(*args, **kwargs)

    def end_exit_call(self, exc=None):
        """End the exit call.

        """
        with self.log_exceptions():
            if self.exit_call:
                self.bt.end_exit_call(exc)
