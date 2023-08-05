"""
interfaces.events is the first default interface mechanism. It provides a
system for referencing and using asyincio events by name.
"""
from functools import partial
from asyncio import Event

from ..context import get_context

context_datastore_key = "events"


def get_event(id, context=None):
    """
    Retrieves an asyncio event object by name, creating one if necessary.

    This method is thread-safe.

    :param id: The string ID of the event to get, or to create.
    :param context: The optional context to use. Otherwise the current
        thread’s context will be used.

    :returns: The asyncio event corresponding to the given id.
    """
    if context is None:
        context = get_context()
    evdata, lock = context.get_interface_data(context_datastore_key)
    with lock:
        if id not in evdata:
            evdata[id] = Event(loop=context.get_event_loop())
        return evdata[id]


def set_event_threadsafe(id, context=None):
    """
    Schedules :meth:`set_event()` to be run in the current context's
    event loop.

    This method is thread-safe.

    :param id: The string ID of the event to set.
    :param context: The optional context to use. Otherwise the current
        thread’s context will be used.
    """
    if context is None:
        context = get_context()
    context.get_event_loop().call_soon_threadsafe(partial(set_event, id, context))


def set_event(eid, context=None):
    """
    Triggers :meth:`set()` on the asyncio event indicated by id, creating
    one if necessary.

    :param id: The string ID of the event to set.
    :param context: The optional context to use. Otherwise the current
        thread’s context will be used.
    """
    if context is None:
        context = get_context()
    evdata, lock = context.get_interface_data(context_datastore_key)
    with lock:
        if eid not in evdata:
            evdata[eid] = Event()
        evdata[eid].set()


def clear_event_threadsafe(eid, context=None):
    """
    Schedules :meth:`clear_event()` to be run in the current context's
    event loop.

    This method is thread-safe.

    :param id: The string ID of the event to clear.
    :param context: The optional context to use. Otherwise the current
        thread’s context will be used.
    """
    if context is None:
        context = get_context()
    context.get_event_loop().call_soon_threadsafe(partial(clear_event, eid, context))


def clear_event(eid, context=None):
    """
    Triggers :meth:`clear()` on the asyncio event indicated by id, creating
    one if necessary.

    :param id: The string ID of the event to clear.
    :param context: The optional context to use. Otherwise the current
        thread’s context will be used.
    """
    if context is None:
        context = get_context()
    evdata, lock = context.get_interface_data(context_datastore_key)
    with lock:
        if eid not in evdata:
            evdata[eid] = Event()
        evdata[eid].clear()
