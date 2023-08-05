import asyncio
import logging
import functools
import inspect

from .hook_server import HookServer


class Module(HookServer):
    """
    Provide an interface for bundling and externally controlling asyncio coroutines.
    This is intended to be subclassed to create a module for a specific purpose.
    """
    name = "module"
    event_loop = None

    def __init__(self):
        super().__init__()
        self.name = self.__class__.__name__
        self.logger = logging.getLogger('yeti.' + self.name)
        self.tasks = list()
        self.add_hook("end_task", self._finish_task)
        self.add_hook("init", self.module_init)
        self.add_hook("init", self.autorun_coroutines)
        self.add_hook("deinit", self.module_deinit)

    def module_init(self):
        """A default `module_init` hook used for initializing the module, and starting any coroutines."""
        self.logger.warn("module_init: Override me!")

    def module_deinit(self):
        """A default `module_deinit` hook used for freeing any used resources."""
        pass

    def start(self, loop=None):
        """
        Start module operation. It configures the asyncio event loop to use for runtime, and
        calls the `module_init` hook to get things running.

        :param loop: An optional event loop to use for module run.
        """
        if loop is None:
            self.event_loop = asyncio.get_event_loop()
        else:
            self.event_loop = loop
        try:
            self.call_hook("init", supress_exceptions=False)
        except Exception as e:
            self.call_hook("exception", e)

        self.logger.info("Finished module init.")

    def stop(self):
        """
        This is used to stop module operation. It cancels all running coroutines and calls the `module_deinit`
        hook to stop everything
        """
        self.call_hook("deinit")
        for task in self.tasks:
            task.cancel()
        self.event_loop = None
        self.logger.info("Finished module deinit.")

    def start_coroutine(self, coroutine):
        """
        Schedule an asyncio coroutine in the module's event loop, and add hooks to handle coroutine failure.

        :param coroutine: The asyncio coroutine to schedule.
        """
        if self.event_loop is None:
            raise ValueError("No event loop setup")
        task = asyncio.async(coroutine)
        task.add_done_callback(functools.partial(self.call_hook, "end_task"))
        self.add_hook("deinit", task.cancel)
        self.call_hook("add_task", task)
        self.tasks.append(task)

    def autorun_coroutines(self):
        for name, obj in inspect.getmembers(self):
            if hasattr(obj, "autorun") and obj.autorun:
                self.start_coroutine(obj())

    def _finish_task(self, fut):
        try:
            if fut.exception():
                if not self.call_hook("exception", fut.exception()):
                    return fut.result()
        except asyncio.CancelledError:
            pass

def autorun_coroutine(func):
    """
    A decorator that sets the coroutine to schedule automatically upon module init.
    """
    func.autorun = True
    return func