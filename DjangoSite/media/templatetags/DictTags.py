import datetime
import typing

from django import template
from django.conf import settings as django_settings
from django.core.paginator import Paginator
from yaml import Loader, load

from ..models import Movie, TVShow
from ..utils import MINIMUM_YEAR

register = template.Library()

TAG_ORDER = {}
TAG_SECTIONS = {}
with open(django_settings.SYNC_PATH / "config" / "Genres.yml", encoding="ascii") as fp:
    YAML_FILE = load(fp, Loader)
    TAG_SECTIONS = YAML_FILE["Tag Sections"]
    TAG_ORDER = YAML_FILE["Tag Order"]


@register.filter()
def Ratio(obj):
    return f"{((obj["Match"]["Runtime"]) / obj["Size"]):0.2f}"


def ObjFromDict(d) -> typing.Any:
    obj = d
    if isinstance(d, dict) and d:
        obj = ObjFromDict(list(d.keys())[0])
    return obj


@register.filter
def HasAttr(iterDict, attrName) -> bool:
    return hasattr(ObjFromDict(iterDict), attrName)


@register.filter
def TagOrder(_tag):
    yield from TAG_ORDER


@register.filter
def TagStyle(group: str, active: bool):

    return f"btn btn-{"" if active else 'outline-'}{TAG_SECTIONS[group]} m-1"


@register.filter
def Get(dictionary, key):
    return dictionary.get(key)


@register.filter
def ModelType(obj) -> str:
    return type(obj).__name__


@register.filter(name="rating")
def Rating(number):
    number = int(round(number))
    outStr = "\u200c" * number
    for _ in range(number // 2):
        outStr += "★"
    for _ in range(number % 2):
        outStr += "½"
    for _ in range(5 - (number // 2) - number % 2):
        outStr += "☆"
    return outStr if number != 0 else "\u200c"


@register.simple_tag
def DottedPageRange(p, number, eachSide=1, onEnds=1):
    paginator = Paginator(p.object_list, p.per_page)
    return paginator.get_elided_page_range(  # type: ignore
        number=number, on_each_side=eachSide, on_ends=onEnds
    )


@register.filter
def GetAttrs(obj):
    excludeList = [
        "Downloaded",
        "InfoPage",
        "Link",
        "Logo",
        "Watched",
    ]
    return (
        [
            str(x).replace("_", " ")
            for x in obj[0].__dict__
            if str(x[0]).isupper() and x not in excludeList
        ]
        if obj
        else []
    )


@register.filter(name="times")
def Times(number):
    return range(number)


@register.filter(name="StarRating")
def StarRatings(number):
    return f"{number//2} {'1/2 ' if number % 2 != 0 else ''}stars"


@register.filter(name="IsHalf")
def IsHalf(number):
    return "half" if number % 2 != 0 else "full"


@register.filter
def MinYear(objList):
    minVal = MINIMUM_YEAR
    if objList:
        if isinstance(objList[0], Movie):
            minVal = min(x.Year for x in Movie.objects.all())
        elif isinstance(objList[0], TVShow):
            minVal = min(x.Year for x in TVShow.objects.all())

    return minVal


@register.filter
def InList(val: typing.Any, valList: typing.Iterable):
    return val in valList


@register.filter
def MaxYear(objList):
    maxVal = datetime.datetime.now().year
    if objList:
        if isinstance(objList[0], Movie):
            maxVal = max(x.Year for x in Movie.objects.all())
        elif isinstance(objList[0], TVShow):
            maxVal = max(x.Year for x in TVShow.objects.all())

    return maxVal
