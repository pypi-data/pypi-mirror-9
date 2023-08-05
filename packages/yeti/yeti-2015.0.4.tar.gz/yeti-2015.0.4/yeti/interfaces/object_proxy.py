import asyncio
from functools import partial
from ..context import get_context
from ..module import add_tag, list_tags

_public_method_tag = "public_method"


@asyncio.coroutine
def call_public_coroutine(name, *args, **kwargs):
    obj = get_object(name)
    if obj is not None:
        yield from obj(*args, **kwargs)


def call_public_method(name, *args, **kwargs):
    obj = get_object(name)
    if obj is not None:
        return obj(*args, **kwargs)


def get_object(name):
    context = get_context()
    mods = context.get_modules()
    for mod in mods:
        for obj in mods[mod].tagged_objects.get(_public_method_tag, []):
            obj_name = list_tags(obj)[_public_method_tag].get("name", "")
            if obj_name == name:
                return obj
    return None


def public_object(f=None, prefix="", name=""):

    if f is None:
        return partial(public_object, prefix=prefix, name=name)
    if name == "":
        name = f.__name__
    if prefix != "":
        name = ".".join([prefix, name])

    return add_tag(f, _public_method_tag, {"name": name})