import os
import urllib.request
from pathlib import Path

from django.conf import settings as django_settings
from PIL import Image, UnidentifiedImageError

DEFAULT_IMG = r"https://upload.wikimedia.org/wikipedia/commons/c/c9/Icon_Video.png"
DEFAULT_IMG_PATH = "logos/DefaultIMG.png"


def DownloadImage(modelObj):
    logoIMG = None
    reloadLogo = (
        not modelObj.Logo
        or "http" in modelObj.Logo
        or not os.path.exists(os.path.join(django_settings.STATIC_ROOT, f"{modelObj.Logo}"))
        or "DefaultIMG.png" in modelObj.Logo
    )

    if reloadLogo:
        if "http" in modelObj.Logo or "www" in modelObj.Logo:
            logoIMG = modelObj.Logo
        elif modelObj.InfoPage and modelObj.InfoPage != "None":
            logoIMG = modelObj.InfoPage
        elif ":" in modelObj.Logo:
            logoIMG = DEFAULT_IMG
        else:
            logoIMG = DEFAULT_IMG
        if logoIMG:
            try:
                savePath = (
                    f"logos/{type(modelObj).__name__.lower()}s/{modelObj.Title.replace(':','')}.png"
                    if logoIMG != DEFAULT_IMG
                    else DEFAULT_IMG_PATH
                )
                if savePath != DEFAULT_IMG_PATH:
                    GetImageFromLink(savePath, logoIMG)
                if (Path(django_settings.STATICFILES_DIRS[0]) / f"{savePath}").exists():
                    modelObj.Logo = savePath
                else:
                    print(f"Cant find {savePath}")
                modelObj.save()
            except ConnectionError:
                pass


def GetImageFromLink(savePath, requestImg):
    tempPath = os.path.join(django_settings.STATICFILES_DIRS[0], "temp.png")

    urllib.request.urlretrieve(
        requestImg,
        tempPath,
    )
    try:
        img = Image.open(tempPath)
        imScale = 240 / img.size[1]
        newSize = round(img.size[0] * imScale), round(img.size[1] * imScale)
        img = img.resize(newSize)
        localPath = os.path.join(django_settings.STATICFILES_DIRS[0], f"{savePath}")
        img.save(localPath)
        os.remove(tempPath)
    except UnidentifiedImageError:
        print("IMG Failed", savePath)
