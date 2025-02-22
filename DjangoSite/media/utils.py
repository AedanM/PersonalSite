# pylint: disable=C0103
import datetime
import random
from typing import Callable

from thefuzz import fuzz

MINIMUM_YEAR = 1900

FEATURES = ["Watched", "Downloaded", "New", "Ready"]


def GetTest(tagName) -> Callable:
    # pylint: disable = C3001
    match (tagName):
        case "Watched":
            test = lambda x: x.Watched
        case "Downloaded":
            test = lambda x: x.Downloaded
        case "New":
            test = lambda x: not x.Downloaded and not x.Watched
        case "Ready":
            test = lambda x: x.Downloaded and not x.Watched
        case _default:
            test = lambda _x: True
    return test


def FuzzStr(obj, query):
    titleFuzz = fuzz.partial_ratio(query.lower(), obj.Title.lower())
    tagFuzz = max(fuzz.partial_ratio(query.lower(), tag.lower()) for tag in obj.GenreTagList)
    titleFuzz = titleFuzz * 1.5 if titleFuzz > 75 else titleFuzz
    return max(titleFuzz, tagFuzz)


def CheckTags(x, tagList):
    return all(tag in x.GenreTagList for tag in tagList.split(",") if tag)


def ExcludeTags(x, tagList):
    return any(tag in x.GenreTagList for tag in tagList.split(",") if tag)


def FilterTags(tagList, objList, include):
    if tagList:
        for feature in FEATURES:
            if feature in tagList:
                test = GetTest(feature)
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


def SearchFunction(subStr, tagStr):
    return all(FuzzStr(subStr, tag) > 75 for tag in tagStr.split(","))


def SortFunction(obj, key: str):
    outObj = None
    key = key.replace(" ", "_")
    match (key):
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


def ExtractYearRange(request, objList):
    minYear = min(x.Year for x in objList) if "Year" in dir(objList[0]) else MINIMUM_YEAR
    yearRange = range(
        int(request.GET.get("minYear", minYear)),
        int(request.GET.get("maxYear", datetime.datetime.now().year)) + 1,
    )
    if "Year" in dir(objList[0]):
        objList = [x for x in objList if x.Year in yearRange]

    return yearRange, objList
