import os
import urllib.request
from PIL import Image
from wikipedia import wikipedia  # type:ignore

from django.conf import settings as django_settings


def DownloadImage(modelObj):
    relevantPics = None
    if (
        not modelObj.Logo
        or "http" in modelObj.Logo
        or not os.path.exists(os.path.join(django_settings.STATIC_ROOT, f"{modelObj.Logo}"))
    ):
        if "http" in modelObj.Logo and "@" not in modelObj.Logo:
            relevantPics = [modelObj.Logo]
        elif "wikipedia" in modelObj.InfoPage:
            try:
                searchTitle = modelObj.InfoPage.split("/wiki/")[-1]
                m = wikipedia.WikipediaPage(searchTitle)  # type:ignore
                relevantPics = [
                    x for x in m.images if ".svg" not in x and ("title" in x or "logo" in x)
                ]
                if not relevantPics:
                    relevantPics = [x for x in m.images if ".svg" not in x]
            except:
                pass
        else:
            relevantPics = [modelObj.InfoPage]
        if relevantPics:
            try:
                urllib.request.urlretrieve(
                    relevantPics[0],
                    "temp.png",
                )
                img = Image.open("temp.png")
                imScale = 480 / img.size[0]
                newSize = round(img.size[0] * imScale), round(img.size[1] * imScale)
                img = img.resize(newSize)
                savePath = f"logos/{modelObj.Title.replace(':','-')}.png"
                localPath = os.path.join(django_settings.STATICFILES_DIRS[0], f"{savePath}")
                img.save(localPath)
                os.remove("temp.png")
                setattr(modelObj, "Logo", savePath)
                modelObj.save()
            except ConnectionError:
                pass
