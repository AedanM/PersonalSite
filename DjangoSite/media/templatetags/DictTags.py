from django import template
import typing
import os
from django.conf import settings as django_settings
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
import numpy as np

register = template.Library()


def ObjFromDict(d) -> typing.Any:
    obj = d
    if type(d) == dict and d:
        obj = ObjFromDict(list(d.values())[0])
    return obj


@register.filter
def HasAttr(iterDict, attrName) -> bool:
    return hasattr(ObjFromDict(iterDict), attrName)


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
