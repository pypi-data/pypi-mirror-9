import yeti
import time
import asyncio
import os
import json
import traceback
import logging
from aiohttp import web

try:
    from yeti.version import __version__
except:
    __version__ = "master"

class WebUILoggerHandler(logging.Handler):

    def __init__(self, handler_func):
        self.handler_func = handler_func
        super().__init__()

    def emit(self, record):
        self.handler_func(record)

class WebUI(yeti.Module):
    """
    A pre-loaded module that provides an elegant interface with which to manage loaded modules.
    """

    def module_init(self):
        logging.getLogger("aiohttp.access").setLevel(logging.WARNING)
        self.context = yeti.get_context()
        self.file_root = os.path.join(os.path.dirname(os.path.realpath(__file__)), "resources")
        self.start_coroutine(self.init_server())
        self.yeti_logger = logging.getLogger("yeti")
        def er_hdl(msg):
            self.context.thread_coroutine(self.error_handler(msg))
        logger_handler = WebUILoggerHandler(er_hdl)
        self.yeti_logger.addHandler(logger_handler)

        self.messages = list()

    next_error_id = 0


    @asyncio.coroutine
    def error_handler(self, message):
        yield from self.clean_messages()
        message_data = {"time": time.monotonic(), "message": message.getMessage(), "level": message.levelname, "id": self.next_error_id}
        self.next_error_id += 1
        self.messages.append(message_data)

    @asyncio.coroutine
    def clean_messages(self):
        #Clean all timed-out messages
        current_time = time.monotonic()
        for message in self.messages[:]:
            if message["time"] + 10 < current_time:
                self.messages.remove(message)

    @asyncio.coroutine
    def json_handler(self, request):
        data_structure = dict()
        data_structure["version"] = __version__
        yield from self.clean_messages()
        data_structure["messages"] = self.messages
        data_structure["next_mid"] = self.next_error_id
        data_structure["modules"] = list()
        for modname in self.context.loaded_modules:
            mod_object = self.context.loaded_modules[modname]
            mod_data = dict()
            mod_data["subsystem"] = modname
            mod_data["description"] = mod_object.__doc__
            if hasattr(mod_object, "loader"):
                mod_data["filename"] = mod_object.loader.module_path
                mod_data["status"] = "Loaded"
                mod_data["fallbacks"] = mod_object.loader.fallback_list
            data_structure["modules"].append(mod_data)
        text = json.dumps(data_structure, allow_nan=False)
        return web.Response(body=text.encode("utf-8"))

    @asyncio.coroutine
    def command_handler(self, request):
        commands = {"load": self.load_command, "load_config": self.load_config, "unload": self.unload_command, "reload": self.reload_command}
        data = yield from request.post()
        try:
            text = yield from commands[data["command"]](data["target"])
        except Exception as e:
            self.logger.error(str(e) + "\n" + traceback.format_exc())
            text = str(e)

        return web.Response(body=text.encode("utf-8"))

    @asyncio.coroutine
    def load_command(self, target):
        if hasattr(self.context, "config_manager"):
            self.context.config_manager.load_module(target, self.context)
        else:
            loader = yeti.ModuleLoader()
            loader.set_context(self.context)
            yield from loader.load_coroutine(target)
        return "Successfully loaded " + target

    @asyncio.coroutine
    def unload_command(self, target):
        yield from self.context.unload_module_coroutine(target)
        return "Successfully unloaded " + target

    @asyncio.coroutine
    def reload_command(self, target):
        all_mods = self.context.get_modules()
        if target == "all":
            target_mods = [all_mods[mod] for mod in all_mods]
        else:
            target_mods = [all_mods[target], ]
        for mod in target_mods:
            if hasattr(mod, "loader"):
                yield from mod.loader.reload_coroutine()
        return "Successfully reloaded " + target

    @asyncio.coroutine
    def load_config(self, path):
        for module in self.context.get_modules():
            yield from self.context.unload_module_coroutine(module)
        if not hasattr(self.context, "config_manager"):
            self.context.config_manager = yeti.ConfigManager()
        self.context.config_manager.parse_config(path)
        self.context.config_manager.load_startup_mods(self.context)
        return "Successfully reloaded config file " + path

    @asyncio.coroutine
    def forward_request(self, request):
        return web.HTTPFound("/index.html")

    @asyncio.coroutine
    def init_server(self):
        app = web.Application()
        app.router.add_route("GET", "/api/json", self.json_handler)
        app.router.add_route("POST", "/api/command", self.command_handler)
        app.router.add_route("GET", "/", self.forward_request)
        app.router.add_static("/", self.file_root)
        self.srv = yield from self.event_loop.create_server(app.make_handler(), port=5800)

        self.logger.info("Yeti WebUI started at  http://127.0.0.1:5800/index.html")

    def module_deinit(self):
        self.srv.close()