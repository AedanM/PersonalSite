# pylint: disable=C0103
import datetime
import random
from collections.abc import Callable
from typing import Any

from django.http import HttpRequest
from thefuzz import fuzz

MINIMUM_YEAR = 1900

FEATURES = ["Watched", "Downloaded", "New", "Ready", "Read"]


def GetTest(tagName: str, objSample: Any) -> Callable:
    required = []
    test: Callable
    match tagName:
        case "Read":
            test = lambda x: x.Read  # noqa: E731
            required = ["Read"]
        case "Watched":
            test = lambda x: x.Watched  # noqa: E731
            required = ["Watched"]
        case "Downloaded":
            test = lambda x: x.Downloaded  # noqa: E731
            required = ["Downloaded"]
        case "New":
            test = lambda x: not x.Downloaded and not x.Watched  # noqa: E731
            required = ["Downloaded", "Watched"]
        case "Ready":
            test = lambda x: x.Downloaded and not x.Watched  # noqa: E731
            required = ["Downloaded", "Watched"]
        case _default:
            test = lambda _x: True  # noqa: E731
    for r in required:
        if r not in dir(objSample):
            return lambda _x: False
    return test


def FuzzStr(obj: Any, query: str) -> float:
    titleFuzz = fuzz.partial_ratio(query.lower(), obj.Title.lower())
    tagFuzz = max(fuzz.partial_ratio(query.lower(), tag.lower()) for tag in obj.GenreTagList)
    titleFuzz = titleFuzz * 1.5 if titleFuzz > 75 else titleFuzz
    return max(titleFuzz, tagFuzz)


def CheckTags(x: Any, tagList: str) -> bool:
    return all(tag in x.GenreTagList for tag in tagList.split(",") if tag)


def ExcludeTags(x: Any, tagList: str) -> bool:
    return any(tag in x.GenreTagList for tag in tagList.split(",") if tag)


def FilterTags(tagList: str, objList: list, include: bool) -> tuple[str, list]:
    if tagList:
        for feature in FEATURES:
            if feature in tagList:
                test = GetTest(feature, objList[0])
                objList = [
                    x for x in objList if (test(x) and include) or (not test(x) and not include)
                ]
                tagList = tagList.replace(feature, "").strip()

        if tagList:
            objList = [
                x
                for x in objList
                if (include and CheckTags(x, tagList))
                or (not include and not ExcludeTags(x, tagList))
            ]

    return tagList, objList


def SearchFunction(sub: str, tag: str) -> bool:
    return all(FuzzStr(sub, tag) > 75 for tag in tag.split(","))


def SortFunction(obj: Any, key: str) -> int | float | str:
    outObj = None
    key = key.replace(" ", "_")
    match key:
        case "Title":
            outObj = obj.SortTitle
        case "None":
            outObj = obj
        case "Genre_Tags":
            outObj = len(obj.GenreTagList)
        case "Random":
            outObj = random.random()
        case "Date_Added":
            outObj = obj.id
        case _others:
            outObj = getattr(obj, key)
    return outObj


def ExtractYearRange(request: HttpRequest, objList: list) -> tuple[range, list]:
    minYear = min(x.Year for x in objList) if "Year" in dir(objList[0]) else MINIMUM_YEAR
    yearRange = range(
        int(request.GET.get("minYear", minYear)),
        int(request.GET.get("maxYear", datetime.datetime.now().year)) + 1,
    )
    if "Year" in dir(objList[0]):
        objList = [x for x in objList if x.Year in yearRange]

    return yearRange, objList
