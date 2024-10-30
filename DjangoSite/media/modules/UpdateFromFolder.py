import glob
import logging
import os
import re
from dataclasses import dataclass
from datetime import timedelta
from typing import Any

from django.conf import settings as django_settings
from django.db import models

from ..models import Comic, Movie, Novel, Podcast, TVShow, Youtube

LOGGER = logging.getLogger("UserLogger")


@dataclass
class Media:
    MediaType: str
    Title: str
    Tags: str
    Seasons: set
    Creator: str
    Year: int = 0
    Duration: timedelta = timedelta(seconds=0)
    WikiPage: str = ""
    Length: int = 0

    def __lt__(self, obj):
        if obj.isinstance(Media):
            return (
                self.MediaType < obj.MediaType
                if self.MediaType != obj.MediaType
                else self.Title < obj.Title
            )


def LoadFiles() -> list[Media]:
    pathList = []
    with open(
        os.path.join(django_settings.STATICFILES_DIRS[0], "mediaPaths.csv"), "r", encoding="ascii"
    ) as fp:
        pathList = fp.read().split(",")
    mediaList: list[Media] = []
    for path in pathList:
        splitList = path.replace("\\", "/").split("/")
        if len(splitList) > 2:
            existingMedia = [x.Title for x in mediaList]

            elementType = splitList[1]
            mediaTitle = splitList[-1] if elementType != "TV Shows" else splitList[-3]
            year = 0
            if elementType == "Movies":
                mediaTitle, year = ExtractYear(mediaTitle)
            elif elementType == "Youtube":
                mediaTitle = mediaTitle.split(sep="-")[-1]
            elif elementType == "Comics" and "(" in mediaTitle:
                mediaTitle = mediaTitle.split(sep="(")[-2]
            if elementType != "TV Shows":
                extension = mediaTitle.split(sep=".")[-1]
                mediaTitle = mediaTitle.replace(f".{extension}", "").strip()
            if mediaTitle not in existingMedia:
                mediaList.append(
                    Media(
                        Title=mediaTitle,
                        MediaType=elementType,
                        Tags=",".join(
                            splitList[2:-1] if elementType != "TV Shows" else splitList[2:-3]
                        ),
                        Seasons=set() if elementType != "TV Shows" else set([splitList[-2]]),
                        Creator=(
                            ""
                            if elementType not in ["Youtube", "Podcasts", "Novels", "Comics"]
                            else (
                                splitList[2]
                                if elementType != "Comics"
                                else f"{splitList[2]}:{splitList[3]}"
                            )
                        ),
                        Year=year,
                    )
                )
            else:
                matchedMedia = [x for x in mediaList if x.Title == mediaTitle][0]
                matchedMedia.Seasons.add(splitList[-2])
    return sorted(mediaList)  # type:ignore


def ExtractYear(mediaTitle):
    match = re.search(r"\((\d{4})\)", mediaTitle)
    year = 0
    if match:
        year = int(match.group(1))
        mediaTitle = mediaTitle.replace(f"({year})", "")
    else:
        LOGGER.warning("Unmatched %s", mediaTitle)
    return mediaTitle, year


def FindPaths(root) -> bool:
    pathList = glob.glob(pathname="./**/*", root_dir=root, recursive=True)
    pathList = [x for x in pathList if "." in x.replace("\\", "/").split("/")[-1]]
    with open(
        os.path.join(django_settings.STATICFILES_DIRS[0], "mediaPaths.csv"), "w", encoding="ascii"
    ) as fp:
        fp.write(",".join(pathList))
    return True


def PopulateObjs(mediaList) -> list[Any]:
    objList = []
    for media in mediaList:
        obj: models.Model = None  # type:ignore
        match (media.MediaType):
            case "Movies":
                obj = Movie(
                    Title=media.Title,
                    Genre_Tags=media.Tags,
                    Downloaded=True,
                    Watched=False,
                    Year=media.Year,
                    Duration=media.Duration,
                    InfoPage=media.WikiPage,
                )
            case "TV Shows":
                obj = TVShow(
                    Title=media.Title,
                    Genre_Tags=media.Tags,
                    Downloaded=True,
                    Watched=False,
                    Length=len(media.Seasons),
                    Duration=media.Duration,
                    InfoPage=media.WikiPage,
                )
            case "Youtube":
                obj = Youtube(
                    Title=media.Title,
                    Genre_Tags=media.Tags,
                    Creator=media.Creator,
                    Downloaded=True,
                    Watched=False,
                    Duration=media.Duration,
                    InfoPage=media.WikiPage,
                )
            case "Novels":
                obj = Novel(
                    Title=media.Title,
                    Genre_Tags=media.Tags,
                    Author=media.Creator,
                    Downloaded=True,
                    PageLength=media.Length,
                    InfoPage=media.WikiPage,
                )
            case "Comics":
                obj = Comic(
                    Title=media.Title,
                    Genre_Tags=media.Tags,
                    Company=media.Creator.split(":")[0],
                    Character=media.Creator.split(":")[1],
                    Downloaded=True,
                    PageLength=media.Length,
                    InfoPage=media.WikiPage,
                )
            case "Podcasts":
                obj = Podcast(
                    Title=media.Title,
                    Genre_Tags=media.Tags,
                    Creator=media.Creator,
                    Downloaded=True,
                    Watched=False,
                    Duration=media.Duration,
                    InfoPage=media.WikiPage,
                )
        if obj:
            objList.append(obj)
    return objList


def FilterDupes(mediaList):
    currentObjs = {
        "TV Shows": TVShow.objects.all(),
        "Movies": Movie.objects.all(),
        "Comics": Comic.objects.all(),
        "Novels": Novel.objects.all(),
        "Podcasts": Podcast.objects.all(),
        "Youtube": Youtube.objects.all(),
    }
    mediaList = [x for x in mediaList if x.MediaType != "Tools"]
    for media in mediaList:
        alreadyExists = [x for x in currentObjs[media.MediaType] if x.Title == media.Title]
        if alreadyExists:
            mediaList.remove(media)
    return mediaList


def UpdateFromFolder(folder, useFile, save) -> str:
    if not useFile:
        LOGGER.warning("Loading Paths")
        FindPaths(root=folder)
        LOGGER.warning("Paths Found")
    media: list[Media] = LoadFiles()
    LOGGER.warning("Files Loaded")
    media = FilterDupes(mediaList=media)
    LOGGER.warning("Objects Filtered")
    mediaObjs: list[models.Model] = PopulateObjs(mediaList=media)
    LOGGER.warning("Objects Populated")
    # mediaObjs = FindWikiPage(mediaList=mediaObjs)
    if save:
        for m in mediaObjs:
            m.save()
    return "\n".join([str(x) for x in media])
