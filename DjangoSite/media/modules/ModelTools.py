import logging
import random
import urllib.parse
import urllib.request
from pathlib import Path

from django.conf import settings as django_settings
from PIL import Image, UnidentifiedImageError

from .ImgResize import BackgroundResize
from .Utils import MakeStringSystemSafe

LOGGER = logging.getLogger("UserLogger")

DEFAULT_IMG = r"https://upload.wikimedia.org/wikipedia/commons/c/c9/Icon_Video.png"
DEFAULT_IMG_PATH = "logos/DefaultIMG.png"


def DownloadImage(modelObj):

    logoIMG = None
    reloadLogo = (
        not modelObj.Logo
        or "http" in modelObj.Logo
        or not (Path(django_settings.STATIC_ROOT) / modelObj.Logo).exists()
        or "DefaultIMG.png" in modelObj.Logo
    )

    if reloadLogo:
        LOGGER.info("Downloading new logo for %s", modelObj.Title)
        logoIMG = modelObj.Logo
        if logoIMG:
            try:
                savePath = (
                    f"logos/{type(modelObj).__name__.lower()}s/{MakeStringSystemSafe(modelObj.Title)}.png"
                    if logoIMG != DEFAULT_IMG
                    else DEFAULT_IMG_PATH
                )
                if savePath != DEFAULT_IMG_PATH:
                    GetImageFromLink(savePath, logoIMG)
                if (Path(django_settings.STATICFILES_DIRS[0]) / f"{savePath}").exists():
                    modelObj.Logo = savePath
                else:
                    modelObj.Logo = DEFAULT_IMG_PATH
                    LOGGER.error("Defaulting %s IMG Path", modelObj.Logo)
                modelObj.save()
            except ConnectionError:
                pass
        else:
            modelObj.Logo = DEFAULT_IMG
            modelObj.save()
    return modelObj.Logo != DEFAULT_IMG


def GetImageFromLink(savePath, requestImg):

    tempPath = Path(django_settings.STATICFILES_DIRS[0]) / f"temp-{random.randint(0,10000)}.png"
    try:
        urllib.request.urlretrieve(
            requestImg,
            str(tempPath),
        )
    except ValueError:
        try:
            urllib.request.urlretrieve(
                urllib.parse.quote(requestImg).replace("%3A", ":"),
                str(tempPath),
            )
        except ValueError:
            return
    try:
        img = Image.open(str(tempPath))
        imScale = 320 / img.size[0]
        newSize = round(img.size[0] * imScale), round(img.size[1] * imScale)
        img = img.resize(newSize)
        localPath = Path(django_settings.STATICFILES_DIRS[0]) / savePath
        img.save(localPath)
        if "tvshows" in str(localPath):
            BackgroundResize(img=localPath)  #
        LOGGER.info("New IMG saved to %s", savePath)
    except UnidentifiedImageError:
        if tempPath.exists():
            LOGGER.error("Resize Failed @ %s", savePath)
        else:
            LOGGER.error("IMG Failed @ %s", requestImg)
    if tempPath.exists():
        tempPath.unlink()


def SortTags(obj):
    tagList = [x.strip() for x in obj.Genre_Tags.split(",")]
    obj.Genre_Tags = ",".join(sorted(tagList))
    obj.save()
