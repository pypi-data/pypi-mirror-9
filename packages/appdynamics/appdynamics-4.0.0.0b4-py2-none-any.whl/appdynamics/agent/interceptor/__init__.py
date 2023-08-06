import sys


def add_hook(agent):
    """Add the module interceptor hook for AppDynamics, if it's not already registered.

    """

    interceptor = ModuleInterceptor(agent)
    sys.meta_path.append(interceptor)
    return interceptor


class ModuleInterceptor(object):
    """Intercepts finding and loading modules in order to monkey patch them on load.

    """

    def __init__(self, agent):
        super(ModuleInterceptor, self).__init__()
        self.agent = agent
        self.module_hooks = {}
        self.intercepted_modules = set()

    def find_module(self, full_name, path=None):
        if full_name in self.module_hooks:
            return self
        return None

    def load_module(self, name):
        # Remove the module from the list of hooks so that we never see it again.
        hooks = self.module_hooks.pop(name, [])

        if name in sys.modules:
            # Already been loaded. Return it as is.
            return sys.modules[name]

        self.agent.logger.debug('Intercepting import %s', name)

        __import__(name)  # __import__('a.b.c') returns <module a>, not <module a.b.c>
        module = sys.modules[name]  # ...so get <module a.b.c> from sys.modules

        self._intercept_module(module, hooks)
        return module

    def call_on_import(self, module_name, cb):
        if module_name in sys.modules:
            self._intercept_module(sys.modules[module_name], [cb])
        else:
            self.module_hooks.setdefault(module_name, [])
            self.module_hooks[module_name].append(cb)

    def _intercept_module(self, module, hooks):
        try:
            for hook in hooks:
                self.agent.logger.debug('Running %s hook %r', module.__name__, hook)
                hook(self.agent, module)
            self.intercepted_modules.add(module)
        except:
            self.agent.logger.exception('Exception in %s hook.', module.__name__)

            # Re-import to ensure the module hasn't been partially patched.
            self.agent.logger.debug('Re-importing %s after error in module hook', module.__name__)
            reload(module)
