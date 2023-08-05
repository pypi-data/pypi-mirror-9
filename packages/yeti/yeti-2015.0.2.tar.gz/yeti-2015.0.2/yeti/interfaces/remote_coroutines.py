import asyncio
from ..context import get_context
from ..module import add_tag

_public_coroutine_tag = "public_coroutine"

@asyncio.coroutine
def call_public_coroutine(name, *args, **kwargs):
    context = get_context()
    mods = context.get_modules()
    for mod in mods:
        for coro in mods[mod].tagged_coroutines.get(_public_coroutine_tag, []):
            if coro.__name__ == name:
                yield from coro(*args, **kwargs)
                return


def public_coroutine(f):
    return add_tag(f, "public_coroutine")