import logging
import importlib
import traceback
import inspect
import asyncio
import sys

logger = logging.getLogger('yeti.module_loader')

class ModuleLoadError(Exception):
    """This error is raised for errors during module load"""
    def __init__(self, name, message):
        super().__init__(name + ": " + message)


class ModuleUnloadError(Exception):
    """This error is raised for errors during module unload"""
    def __init__(self, name, message):
        super().__init__(name + ": " + message)


class ModuleLoader(object):
    """
    This dynamically imports modules from the filesystem and loads them into a context.
    This also contains mechanisms for loading fallback modules upon module failure.
    """
    def __init__(self):

        self.fallback_list = list()
        self.fallback_index = 0

        self.module_path = ""
        self.module_name = ""
        self.module_object = None
        self.module_import = None
        self.module_context = None

        self.logger = logger

    def set_context(self, context):
        """
        Sets the context for the module loader to load modules into.

        :param context: The context to use for the module
        """
        self.module_context = context


    def get_context(self):
        """
        :returns: The context currently set for the loader.
        """
        if self.module_context is None:
            raise ValueError("No context set.")
        return self.module_context

    def get_module(self):
        """
        :returns: The currently loaded module object.
        """
        return self.module_object

    def reload(self):
        """
        Schedules reload_coroutine to be run in the context currently set for the module_loader.
        This method is thread-safe.
        """
        self.get_context().thread_coroutine(self.reload_coroutine())

    @asyncio.coroutine
    def reload_coroutine(self):
        """
        This unloads any existing module object and loads the next available module in the callback list.
        """
        yield from self.load_coroutine()

    def add_fallback(self, fallback):
        """
        Add a filename to the fallback list.

        :param fallback: The filename to add to the fallback list.
        """
        self.fallback_list.append(fallback)

    def set_fallback(self, fallback_list):
        """
        Replaces the current fallback list with a copy of fallback_list.

        :param fallback_list: The list of filenames to use for the fallback list.
        """
        self.fallback_list = fallback_list[:]

    @asyncio.coroutine
    def load_coroutine(self, module_path=None):
        """
        Loads a module into the loader, taking the filename from the top of the fallback_list.

        Prior to module loading, it will unload any loaded module.

        If given module_path, it will try to find it in the current fallback list. If it fails, it will create a new
        fallback_list with module_path.

        It then iterates through fallback_list, loading modules until one completes successfully.

        :param module_path: The (optional) module filename to use.
        """

        #Start by unloading any previously loaded module
        yield from self.unload_coroutine()

        #Setup module fallback lists

        #If a module was actually specified, try to find it in fallback_list, otherwise,
        # wipe fallback_list and add module_path
        if module_path is not None:
            if module_path in self.fallback_list:
                self.fallback_index = self.fallback_list.index(module_path)
            else:
                self.fallback_list = [module_path]
                self.fallback_index = 0

        #Loop through fallback_list and try to find a module that will load.
        while True:

            #Do we have any more to try?
            if self.fallback_index >= len(self.fallback_list):
                raise ModuleLoadError(self.module_name, "No files left to try and load in the fallback list")

            #Lets try this module, the one selected by fallback_index
            file_to_load = self.fallback_list[self.fallback_index]
            try:

                logger.debug("Loading " + file_to_load)

                #Reload the module if it is already loaded, otherwise import it anew..
                if file_to_load in sys.modules:
                    self.module_import = sys.modules[file_to_load]
                    importlib.reload(self.module_import)
                else:
                    self.module_import = importlib.import_module(file_to_load)

                #Get the module class
                module_class = None
                for name, obj in inspect.getmembers(self.module_import):
                    if inspect.isclass(obj) and hasattr(obj, "module_init"):
                        module_class = obj
                        break
                else:
                    raise ModuleLoadError("Loader", "No compatible module class found in " + file_to_load)

                #Initialize the actual module object
                self.module_object = module_class()

                #Get the module's name and file name
                self.module_name = self.module_object.name
                self.module_path = file_to_load
                self.logger = self.module_object.logger

                #Add control hooks
                self.module_object.add_hook("exception", self._exception_handler)

                #embed self
                self.module_object.loader = self

                #Add module to the current context:
                yield from self.module_context.load_module_coroutine(self.module_object)

                #Yay, we must have been successful!
                break

            except Exception as e:
                #Oops, something happened. We must try the next one on the fallback list!
                self.logger.error("Error loading module: " + file_to_load + ": " + str(e) + "\n" + traceback.format_exc())
                self.fallback_index += 1

    def load(self, module_path=None):
        """Schedules :meth:`load_coroutine` to be run."""
        self.get_context().thread_coroutine(self.load_coroutine(module_path))

    @asyncio.coroutine
    def unload_coroutine(self):
        """Unload the currently loaded module"""
        if self.module_object is not None:
            yield from self.module_context.unload_module_coroutine(self.module_name)
            self.module_object = None

    def unload(self):
        """Schedules :meth:`unload_coroutine` to be run."""
        self.get_context().thread_coroutine(self.unload_coroutine())

    def _exception_handler(self, exception):
        #Oops, something happened
        self.logger.error("Error in module run: {}: {}\n {}".format(self.module_path, str(exception), "".join(traceback.format_tb(exception.__traceback__))))

        #Try to load a replacement module.
        try:
            self.replace_faulty()
        except ModuleLoadError as e:
            logger.error(e)

    @asyncio.coroutine
    def replace_faulty_coroutine(self):
        """Replace a faulty module with the next in line, aka increment fallback_index and trigger load()"""
        self.fallback_index += 1
        try:
            yield from self.load_coroutine()
        except Exception as e:
            self.logger.error("Error replacing faulty module: " + str(e))

    def replace_faulty(self):
        """Schedules :meth:`replace_faulty_coroutine` to be run."""
        self.get_context().thread_coroutine(self.replace_faulty_coroutine())