import os
import typing

import matplotlib
from django import template
from django.conf import settings as django_settings
from django.core.paginator import Paginator

from ..models import Movie, TVShow

matplotlib.use("Agg")
# pylint:disable=C0413
import matplotlib.pyplot as plt

register = template.Library()


def ObjFromDict(d) -> typing.Any:
    obj = d
    if isinstance(d, dict) and d:
        obj = ObjFromDict(list(d.keys())[0])
    return obj


@register.filter
def HasAttr(iterDict, attrName) -> bool:
    return hasattr(ObjFromDict(iterDict), attrName)


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


@register.filter
def MakeChart(iterDict, chartType) -> str:
    outPath = os.path.join(
        django_settings.STATICFILES_DIRS[0], f"images/charts/mediaChart-{chartType}.png"
    )
    sizes = []
    labels = []
    for label, media in iterDict.items():
        labels.append(label)
        match (chartType):
            case "Duration":
                sizes.append(
                    sum(
                        x.Duration.total_seconds()
                        for x in [y for y in media.values()]
                        if "Duration" in dir(x)
                    )
                )
            case "Count":
                sizes.append(len(media.values()))

    plt.pie(sizes, labels=labels, shadow=True, textprops={"color": "white"})
    plt.savefig(outPath, transparent=True)
    plt.close()
    return f"images/charts/mediaChart-{chartType}.png"


@register.simple_tag
def DottedPageRange(p, number, eachSide=1, onEnds=1):
    paginator = Paginator(p.object_list, p.per_page)
    return paginator.get_elided_page_range(  # type: ignore
        number=number, on_each_side=eachSide, on_ends=onEnds
    )


@register.filter
def GetAttrs(obj):
    ExcludeList = [
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
            if str(x[0]).isupper() and x not in ExcludeList
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
    minVal = 1900
    if isinstance(objList[0], Movie):
        minVal = min(x.Year for x in Movie.objects.all())
    elif isinstance(objList[0], TVShow):
        minVal = min(x.Year for x in TVShow.objects.all())

    return minVal


@register.filter
def MaxYear(objList):
    maxVal = 1900
    if isinstance(objList[0], Movie):
        maxVal = max(x.Year for x in Movie.objects.all())
    elif isinstance(objList[0], TVShow):
        maxVal = max(x.Year for x in TVShow.objects.all())

    return maxVal
