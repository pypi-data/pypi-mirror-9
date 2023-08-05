import logging

from .module_loader import ModuleLoader

logger = logging.getLogger('yeti.ConfigManager')


class ConfigurationError(Exception):
    pass


class ConfigManager(object):
    """
    Uses instances of :class:`ModuleLoader` to load modules from reference lists in a configuration file.
    """

    _STARTUP_MOD_SECTION = "StartupMods"
    _config_path = ""

    def __init__(self):
        self.config_structure = None
        self.module_loaders = dict()

    def load_startup_mods(self, context):
        """
        Find all modules in the "StartupMods" section of the config file, and load them with instances of :class:`ModuleLoader`
        into the specified context.

        :param context: The context to load the modules into.
        """

        if self.config_structure is None:
            raise ConfigurationError("No config file loaded.")
        for module_name in self.config_structure[self._STARTUP_MOD_SECTION]:
            self.load_module(module_name, context)

    def load_module(self, name, context):
        """
        This uses a loaded config file to generate a fallback list and use a :class:`ModuleLoader` to load the module.

        :param name: The name reference of the module to load.
        :param context: The context to load the module into.

        :returns: The created :class:`ModuleLoader`
        """

        #Add reference to context for introspection.
        context.config_manager = self

        if self.config_structure is None:
            fallback_list = [name]
            fallback_index = 0

        #is it a subsystem name?
        elif name in self.config_structure:
            fallback_list = self.config_structure[name]
            fallback_index = 0

        #no? must be a filename then.
        else:
            #Search for filename in loaded config
            for subsystem_config in self.config_structure:
                if subsystem_config != self._STARTUP_MOD_SECTION and name in self.config_structure[subsystem_config]:
                    #We found it! set the fallback list
                    fallback_list = self.config_structure[subsystem_config]
                    fallback_index = fallback_list.index(name)
                    break

            #If we still don't have a fallback list, just make one up and go!
            else:
                fallback_list = [name]
                fallback_index = 0

        module_loader = ModuleLoader()
        module_loader.set_context(context)
        module_loader.fallback_list = fallback_list
        module_loader.fallback_index = fallback_index
        module_loader.load()
        self.module_loaders[name] = module_loader
        return module_loader

    def parse_config(self, path):
        """
        Parse the config file.

        :param path: The file path of the config file to parse.

        :returns: The dictionary of the parsed config file.
        """

        if path == "":
            path = self._config_path
        self._config_path = path

        #Open the file
        f = open(path)
        section = None
        parsed_config = dict()

        #for each line in file:
        for line in f:
            #Get rid of extra spaces and carriage-returns
            line = line.rstrip('\r\n')

            #If there is a comment on the line, get rid of everything after the comment symbol and trim whitespace
            #Example: hi there #This is a comment
            if "#" in line:
                line, comment = line.split("#", 1)
                line = line.strip()

            #If there is a section header on the line, figure out what it's name is, and save it
            if "[" in line:
                #Example: [StartupMods]
                section = line.split("[", 1)[1].split("]", 1)[0]
                parsed_config[section] = list()

            #If there is no section header, than the line must contian data, so save it under the current section
            else:
                if line is not "":
                    parsed_config[section].append(line)

        #Message the system
        logger.info("Finished parsing " + path)
        self.config_structure = parsed_config
        return parsed_config
