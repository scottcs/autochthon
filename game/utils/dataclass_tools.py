"""Utility to add slots to dataclasses, from Eric V. Smith.

https://github.com/ericvsmith/dataclasses
https://mail.python.org/archives/list/python-ideas@python.org/thread/U6IFJNMPNJMOICMI3OSVRCRSZDMZ3V4M/

"""
import dataclasses
import typing


def add_slots(cls: typing.Any) -> typing.Any:
    """Add slots to a dataclass."""
    # Need to create a new class, since we can't set __slots__
    #  after a class has been created.

    # Make sure __slots__ isn't already set.
    if "__slots__" in cls.__dict__:
        raise TypeError(f"{cls.__name__} already specifies __slots__")

    # Create a new dict for our new class.
    cls_dict = dict(cls.__dict__)
    field_names = tuple(f.name for f in dataclasses.fields(cls))
    cls_dict["__slots__"] = field_names
    for field_name in field_names:
        # Remove our attributes, if present. They'll still be
        #  available in _MARKER.
        cls_dict.pop(field_name, None)
    # Remove __dict__ itself.
    cls_dict.pop("__dict__", None)
    # And finally create the class.
    qualname = getattr(cls, "__qualname__", None)
    cls = type(cls)(cls.__name__, cls.__bases__, cls_dict)
    if qualname is not None:
        cls.__qualname__ = qualname
    return cls


def slotted_dataclass(cls: typing.Any) -> typing.Any:
    """Decorator to turn a class into a dataclass with slots."""
    return add_slots(dataclasses.dataclass(cls))
