"""
This is an interface designed to make it easier to communicate
gamemode between modules.
"""

from ..context import get_context
from ..module import add_tag, copy_tags
import asyncio
import wpilib

context_data_key = "gamemode"

DISABLED = 0
TELEOPERATED = 1
AUTONOMOUS = 2


def set_gamemode(mode, context=None):
    """
    Sets the current gamemode and releases any coroutines waiting for it.

    :param mode: The gamemode to set.
    :param context: The optional context to use for data storage. If none, the current
        thread’s context will be used.
    """
    if context is None:
        context = get_context()
    data, lock = context.get_interface_data(context_data_key)
    with lock:
        if mode != data.get("mode", " "):
            data["last_change"] = wpilib.Timer.getFPGATimestamp()
        data["mode"] = mode
        context.thread_coroutine(_on_gamemode_set(mode, context))


@asyncio.coroutine
def _on_gamemode_set(mode, context):
    """
    Sets all saved events for the given gamemode
    """
    data, lock = context.get_interface_data(context_data_key)
    events = data.get("events-mode-" + str(mode), None)
    if events is not None:
        for event in events:
            event.set()

#Gamemode Conditionals#############################


def _is_gamemode(modes, context=None):
    """
    Is the robot in one of the given gamemodes?
    """
    if not (isinstance(modes, tuple) or isinstance(modes, list)):
        modes = [modes, ]

    if context is None:
        context = get_context()
    data, lock = context.get_interface_data(context_data_key)

    return data.get("mode", "") in modes


def is_enabled():
    """
    :returns: True if the robot is Enabled.
    """
    return _is_gamemode((AUTONOMOUS, TELEOPERATED))


def is_teleop():
    """
    :returns: True if the robot is in Teleoperated mode.
    """
    return _is_gamemode(TELEOPERATED)


def is_autonomous():
    """
    :returns: True if the robot is in Autonomous mode.
    """
    return _is_gamemode(AUTONOMOUS)


def is_disabled():
    """
    :returns: True if the robot is Disabled.
    """
    return _is_gamemode(DISABLED)

#Gamemode Wait Coroutines############################


@asyncio.coroutine
def wait_for_gamemode(modes, context=None):
    """
    Waits until one of the indicated modes is set.

    This is an asyncio coroutine.

    :param modes: One or more modes to wait for.
    :param context: The optional context to use for data storage. If none, the current
        thread’s context will be used.
    """

    if not (isinstance(modes, tuple) or isinstance(modes, list)):
        modes = [modes, ]

    if context is None:
        context = get_context()
    data, lock = context.get_interface_data(context_data_key)

    event = asyncio.Event()

    for mode in modes:
        if mode == data.get("mode", ""):
            return
        events_key = "events-mode-" + str(mode)
        if events_key not in data:
            data[events_key] = list()

        data[events_key].append(event)

    yield from event.wait()

    for mode in modes:
        events_key = "events-mode-" + str(mode)
        data[events_key].remove(event)


@asyncio.coroutine
def wait_for_disabled(context=None):
    """
    Waits until the disabled mode is set.

    This is an asyncio coroutine.

    :param context: The optional context to use for data storage. If none, the current
        thread’s context will be used.
    """
    yield from wait_for_gamemode(DISABLED, context=context)


@asyncio.coroutine
def wait_for_teleop(context=None):
    """
    Waits until the teleoperated mode is set.

    This is an asyncio coroutine.

    :param context: The optional context to use for data storage. If none, the current
        thread’s context will be used.
    """
    yield from wait_for_gamemode(TELEOPERATED, context=context)


@asyncio.coroutine
def wait_for_autonomous(context=None):
    """
    Waits until the autonomous mode is set.

    This is an asyncio coroutine.

    :param context: The optional context to use for data storage. If none, the current
        thread’s context will be used.
    """
    yield from wait_for_gamemode(AUTONOMOUS, context=context)


@asyncio.coroutine
def wait_for_enabled(context=None):
    """
    Waits until either the autonomous mode or the teleoperated mode is set.

    This is an asyncio coroutine.

    :param context: The optional context to use for data storage. If none, the current
        thread’s context will be used.
    """
    yield from wait_for_gamemode((TELEOPERATED, AUTONOMOUS), context=context)

#Gamemode Coroutine Decorators##########################


def _gamemode_task(f, gamemodes):
    @asyncio.coroutine
    def wrapper_func(*args, **kwargs):
        while True:
            yield from wait_for_gamemode(gamemodes)
            yield from f(*args, **kwargs)
            #Give the rest of the robot a moment to breath before looping
            yield from asyncio.sleep(.05)
    copy_tags(f, wrapper_func)
    add_tag(wrapper_func, "autorun")
    return wrapper_func


def disabled_task(f):
    """
    A decorator function that causes the decorated coroutine to run continually
    when the robot is Disabled.
    """
    return _gamemode_task(f, DISABLED)


def teleop_task(f):
    """
    A decorator function that causes the decorated coroutine to run continually
    when the robot is in Teleoperated Mode.
    """
    return _gamemode_task(f, TELEOPERATED)


def autonomous_task(f):
    """
    A decorator function that causes the decorated coroutine to run continually
    when the robot is in Autonomous Mode.
    """
    return _gamemode_task(f, AUTONOMOUS)


def enabled_task(f):
    """
    A decorator function that causes the decorated coroutine to run continually
    when the robot is Enabled.
    """
    return _gamemode_task(f, (AUTONOMOUS, TELEOPERATED))

#Misc Utils

def gamemode_seconds_elapsed(context=None):
    """
    :param context: The optional context to use for data retrieval.

    :returns: The seconds elapsed since the start of the current gamemode.
    """
    if context is None:
        context = get_context()
    data, lock = context.get_interface_data(context_data_key)
    current_time = wpilib.Timer.getFPGATimestamp()
    return current_time - data.get("last_change", current_time)

