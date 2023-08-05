import wpilib
from robotpy_ext.misc import asyncio_policy
from os.path import join
from .. import Context, ConfigManager
from ..interfaces import gamemode


class YetiRobot(wpilib.IterativeRobot):
    """
    This is a standard robot class that uses the full stack of yeti.
    """

    config_dir = ""
    config_file = "mods.conf"

    #Patch the asyncio policy to use wpilib.Timer.getFPGATime() rather than time.monotonic()
    asyncio_policy.patch_asyncio_policy()

    def robotInit(self):
        #First get the context initialized, as ModuleLoaders use it to run
        self.context = Context()
        self.context.start()

        #Then use a ConfigManager to load modules specified in a configuration file
        config_manager = ConfigManager()
        config_manager.parse_config(join(self.config_dir, self.config_file))
        config_manager.load_startup_mods(self.context)

    def teleopInit(self):
        gamemode.set_gamemode(gamemode.TELEOPERATED, context=self.context)

    def disabledInit(self):
        gamemode.set_gamemode(gamemode.DISABLED, context=self.context)

    def autonomousInit(self):
        gamemode.set_gamemode(gamemode.AUTONOMOUS, context=self.context)

