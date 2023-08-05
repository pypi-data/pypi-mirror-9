class Referee:
    """
    This is for keeping track of used wpilib references, and freeing them if their containing modules get unloaded.
    """

    def __init__(self, module):
        self.module = module
        self.refs = list()
        self.hook = module.add_hook("deinit", self.free_all)

    def watch(self, wpilib_object):
        """Keep track of a wpilib object."""
        if hasattr(wpilib_object, "free"):
            self.refs.append(wpilib_object)

    def free_all(self):
        """Frees all watched wpilib references."""
        for wpilib_object in self.refs:
            wpilib_object.free()
