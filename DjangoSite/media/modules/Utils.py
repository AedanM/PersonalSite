import json
import logging
import os
import re
from pathlib import Path
from pprint import pp
from typing import Any

from django.conf import settings as django_settings
from django.core.exceptions import ObjectDoesNotExist

# pylint: disable=E0402
from ..forms import AlbumForm, ComicForm, MovieForm, NovelForm, PodcastForm, TVForm, YoutubeForm
from ..models import Album, Comic, Movie, Novel, Podcast, TVShow, Youtube
from ..utils import (
    FEATURES,
    ExtractYearRange,
    FilterTags,
    FuzzStr,
    GetTest,
    SearchFunction,
    SortFunction,
)

DEFINED_TAGS: dict = {}
DEFINED_TAGS_TIME = 0.0
FORM_LIST = [MovieForm, TVForm, NovelForm, ComicForm, PodcastForm, YoutubeForm, AlbumForm]
MODEL_LIST = [Movie, TVShow, Novel, Comic, Podcast, Youtube, Album]

LOGGER = logging.getLogger("UserLogger")


def LoadDefinedTags():
    global DEFINED_TAGS_TIME, DEFINED_TAGS  # type:ignore
    DEFINED_TAGS_TIME = os.path.getmtime(django_settings.SYNC_PATH / "config" / "Genres.json")
    with open(django_settings.SYNC_PATH / "config" / "Genres.json", encoding="ascii") as fp:
        DEFINED_TAGS = json.load(fp)
        DEFINED_TAGS.pop("_comment", None)


def MakeStringSystemSafe(
    inputPath: str | Path,
    removeSpaces: bool = True,
) -> str:
    objPath: Path = Path(inputPath)
    stringPath = objPath.stem
    bannedChars = '<>:"/\\|?*'
    if removeSpaces:
        bannedChars += " "
    for bannedChar in bannedChars:
        stringPath = stringPath.replace(bannedChar, "_")

    return str(objPath.parent / (stringPath + objPath.suffix))


def CamelToSentence(text: str) -> str:
    matches = re.finditer(".+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)", text)
    return " ".join([m.group(0) for m in matches])


def ModelDisplayName(model):
    return CamelToSentence(model.__name__ + "s")


def FormMatch(obj):
    return [x for x in FORM_LIST if isinstance(obj, x.Meta.model)][0]


def DetermineForm(request):
    contentType = "Movie"
    if "Year" in request.POST:
        contentType = "Movie"
    elif "Length" in request.POST:
        contentType = "TV"
    elif "Creator" in request.POST:
        if "Link" in request.POST:
            contentType = "Youtube"
        else:
            contentType = "Podcast"
    elif "Author" in request.POST:
        contentType = "Book"
    elif "Character" in request.POST:
        contentType = "Comic"
    elif "Artist" in request.POST:
        contentType = "Album"
    return GetFormAndClass(contentType)


def GetFormAndClass(formType) -> tuple:
    obj = [x for x in MODEL_LIST if formType.replace(" ", "").lower() in x.__name__.lower()][0]
    cls = FormMatch(obj())
    return cls, obj


def FindID(contentID: str) -> Any:
    for model in MODEL_LIST:
        try:
            # pylint: disable=E1101
            obj = model.objects.get(pk=contentID)
        except ObjectDoesNotExist:
            obj = None
        if obj:
            return obj
    return None


def GetAllTags(objType, loggedIn=False) -> dict[str, dict]:
    if os.path.getmtime(django_settings.SYNC_PATH / "config" / "Genres.json") > DEFINED_TAGS_TIME:
        LoadDefinedTags()
    genres = []
    _ = [[genres.append(y) for y in x.GenreTagList] for x in objType.objects.all()]  # type:ignore
    freqDir: dict = {}
    for title, definedList in DEFINED_TAGS.items():
        freqDir[title] = {}
        for i in definedList:
            if genres.count(i) > 0:
                freqDir[title][i] = genres.count(i)
            for feature in FEATURES:
                if i == feature and (loggedIn or i == "Watched"):
                    try:
                        freqDir[title][i] = len(
                            [x for x in objType.objects.all() if GetTest(feature)(x)]
                        )
                    except AttributeError:
                        LOGGER.error("%s not found in %s", feature, objType.__name__)
                elif i == "Watched" and i in dir(objType.objects.all()[0]):
                    freqDir[title][i] = len(
                        [x for x in objType.objects.all() if GetTest(feature)(x)]
                    )

        genres = [x for x in genres if x not in definedList and x != "Downloaded"]
    freqDir["ETC"] = {}
    for i in set(genres):
        freqDir["ETC"][i] = genres.count(i)

    outputDir = {}
    for title, freqList in freqDir.items():
        outputDir[title] = dict(sorted(freqList.items(), key=lambda x: x[1], reverse=True))
    return outputDir


def FilterMedia(request, objType) -> dict:

    # pylint: disable=E1101
    sortKey: str = request.GET.get("sort", "Title")
    reverseSort: bool = request.GET.get("reverse", "false") == "true"
    objList = list(objType.objects.all())
    yearRange, objList = ExtractYearRange(request, objList)

    genre, objList = FilterTags(
        request.GET.get("genre", ""),
        objList,
        include=True,
    )
    exclude, objList = FilterTags(
        request.GET.get("exclude", ""),
        objList,
        include=False,
    )

    if query := request.GET.get("query", None):
        objList = [x for x in objList if SearchFunction(subStr=x, tagStr=query)]
        objList = sorted(objList, key=lambda x: FuzzStr(x, query), reverse=True)
        sortKey = f"Search {query}"
    else:
        if sortKey == "Rating":
            objList = [x for x in objList if x.Rating > 0]
        objList = sorted(objList, key=lambda x: SortFunction(obj=x, key=sortKey))
        if sortKey in ["Rating", "Genre Tags", "Date Added"]:
            objList = list(reversed(objList))
        if reverseSort:
            objList = list(reversed(objList))
    return {
        "type": objType.__name__,
        "sort": sortKey,
        "reverse": reverseSort,
        "obj_list": objList,
        "Tags": GetAllTags(objType=objType, loggedIn=request.user.is_authenticated),
        "filters": {
            "include": genre,
            "exclude": exclude,
            "minYear": yearRange.start,
            "maxYear": yearRange.stop,
        },
        "params": (
            ("?" + "".join(request.get_full_path().split("?")[1:]))
            if request.get_full_path().split("?")[1:]
            else ""
        ),
    }


def GenerateReport(obj, objCount):
    output = {}
    objects = obj.objects.all()
    used = []
    for genre in DEFINED_TAGS["Genres"]:
        output[genre] = sorted(
            [x for x in objects if genre in x.Genre_Tags and x not in used and x.Rating > 0],
            key=lambda x: x.Rating,
            reverse=True,
        )[:objCount]
        used += output[genre]
    return output if len(used) > 0 else {}


LoadDefinedTags()
