import os
import typing

import matplotlib
from django import template
from django.conf import settings as django_settings

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
def ModelType(obj) -> str:
    return type(obj).__name__


@register.filter(name="rating")
def Rating(number):
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
                        [
                            x.Duration.total_seconds()
                            for x in [y for y in media.values()]
                            if "Duration" in dir(x)
                        ]
                    )
                )
            case "Count":
                sizes.append(len(media.values()))

    plt.pie(sizes, labels=labels, shadow=True, textprops={"color": "white"})
    plt.savefig(outPath, transparent=True)
    plt.close()
    return f"images/charts/mediaChart-{chartType}.png"
