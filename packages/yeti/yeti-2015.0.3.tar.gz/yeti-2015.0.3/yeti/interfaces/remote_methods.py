import asyncio
from ..context import get_context
from ..module import add_tag

_public_method_tag = "public_method"
_public_coroutine_tag = "public_coroutine"


@asyncio.coroutine
def call_public_coroutine(name, *args, **kwargs):
    context = get_context()
    mods = context.get_modules()
    for mod in mods:
        for coro in mods[mod].tagged_objects.get(_public_coroutine_tag, []):
            if coro.__name__ == name:
                yield from coro(*args, **kwargs)


def call_public_method(name, *args, **kwargs):
    context = get_context()
    mods = context.get_modules()
    for mod in mods:
        for method in mods[mod].tagged_objects.get(_public_method_tag, []):
            if method.__name__ == name:
                return method(*args, **kwargs)


def public_method(f):
    return add_tag(f, _public_method_tag)


def public_coroutine(f):
    return add_tag(f, _public_coroutine_tag)