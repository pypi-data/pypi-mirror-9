import threading
import asyncio
import logging
import traceback

from .hook_server import HookServer


_contexts = dict()

def set_context(context):
    """
    Sets the context for the current thread.

    :param context: An instance of Context to be saved
    """
    _contexts[threading.current_thread()] = context

def get_context():
    """
    :returns: the context set for that thread.
    """
    return _contexts[threading.current_thread()]

class Context(HookServer):
    """
    This hosts an asyncio event loop in a thread, and contains mechanisms for loading and unloading modules.
    """
    _event_loop = None
    _thread = None

    def __init__(self):
        super().__init__()
        self.loaded_modules = dict()
        self.interface_data = dict()
        self.interface_data_lock = threading.RLock()
        self._event_loop = asyncio.new_event_loop()
        self.logger = logging.getLogger(name="yeti." + self.__class__.__name__)

    def thread_coroutine(self, coroutine, logger=None):
        """
        Schedules coroutine to be run in the context's event loop.
        This function is thread-safe.

        :param coroutine: The coroutine to schedule
        """
        if logger is None:
            logger = self.logger
        self._event_loop.call_soon_threadsafe(asyncio.async, self._error_net(coroutine, logger))

    @asyncio.coroutine
    def _error_net(self, coro, log):
        try:
            yield from coro
        except Exception as e:
            self.logger.error(str(e) + "\n" + traceback.format_exc())

    def get_event_loop(self):
        """
        :returns: The context's event loop
        """
        return self._event_loop

    def get_interface_data(self, interface_id):
        """
        Returns a data tuple stored for the identifier interface_id, creating one if necessary.

        :param interface_id: The string identifier for the data tuple to return

        :returns: A data tuple of type (:class:`dict()` , :class:`threading.RLock()`)
        """
        with self.interface_data_lock:
            if interface_id not in self.interface_data:
                self.interface_data[interface_id] = (dict(), threading.RLock())
            data = self.interface_data[interface_id]
        return data

    def start(self):
        """Spawns a new thread and runs :meth:`.run_forever` in it."""
        if self._thread is None:
            self._thread = threading.Thread(target=self.run_forever)
            self._thread.start()

    def run_forever(self):
        """
        Sets the context for the current thread, and runs the context's event loop forever.
        """
        set_context(self)
        asyncio.set_event_loop(self._event_loop)
        self.call_hook("context_start", self)
        self._event_loop.run_forever()

    def run_for(self, time):
        """
        Sets the context for the current thread, and runs the context's event loop for the specified duration.

        :param time: The time in seconds to run the event loop for.
        """
        set_context(self)
        asyncio.set_event_loop(self._event_loop)
        self.call_hook("context_start", self)
        self._event_loop.run_until_complete(asyncio.sleep(time))

    def stop(self):
        """
        Schedules :meth:`.stop_coroutine` to be run in the context's event loop.
        This method is thread-safe.
        """
        self.thread_coroutine(self.stop_coroutine)

    @asyncio.coroutine
    def stop_coroutine(self):
        """
        Unloads all modules and stops the event loop.
        This method is a coroutine.
        """
        for modname in self.loaded_modules:
            yield from self.unload_module_coroutine(modname)
        self.call_hook("context_stop", self)
        self._event_loop.stop()

    def load_module(self, module):
        """
        Schedules :meth:`.load_module_coroutine` to be run in the context's event loop.
        This method is thread-safe.

        :param module: The module object to load into the context.
        """
        self.thread_coroutine(self.load_module_coroutine(module))

    @asyncio.coroutine
    def load_module_coroutine(self, module):
        """
        Loads module into the context, and errors if we already have one with that name. Triggers :meth:`.start()`.

        :param module: The module object to load into the context.
        """
        if module.name in self.loaded_modules:
            raise ValueError("Already have a module with name {} in this context, cannot add another.")
        self.loaded_modules[module.name] = module
        module.start(loop=self._event_loop)
        self.call_hook("module_load", module)

    def unload_module(self, module_name):
        """
        Schedules :meth:`.unload_module_coroutine()` to be run in the context's event loop.
        This method is thread-safe.

        :param module_name: The the name of the module to be unloaded from the context.
        """
        self.thread_coroutine(self.unload_module_coroutine(module_name))

    @asyncio.coroutine
    def unload_module_coroutine(self, module_name):
        """
        Unloads module_name from the context. Triggers :meth:`.stop()`.

        :param module_name: The name of the module to be unloaded the context.
        """
        if module_name not in self.loaded_modules:
            raise ValueError("Module {} not loaded.".format(module_name))
        self.loaded_modules[module_name].stop()
        self.call_hook("module_unload", self.loaded_modules[module_name])
        del(self.loaded_modules[module_name])

    def get_modules(self):
        return self.loaded_modules.copy()