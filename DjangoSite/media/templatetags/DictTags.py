from django import template
import typing

register = template.Library()


def ObjFromDict(d) -> typing.Any:
    obj = d
    if type(d) == dict:
        obj = ObjFromDict(list(d.values())[0])
    return obj


@register.filter
def HasAttr(iterDict, attrName) -> bool:
    return hasattr(ObjFromDict(iterDict), attrName)
