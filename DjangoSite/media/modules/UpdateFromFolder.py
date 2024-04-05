from dataclasses import dataclass
from datetime import timedelta
from django.conf import settings as django_settings
import os
import glob
from typing import Any
from ..models import Movie, TVShow, Podcast, Book, Youtube


@dataclass
class Media:
    MediaType: str
    Title: str
    Tags: list[str]
    Seasons: set
    Creator: str
    Year: int = 0
    Duration: timedelta = timedelta(seconds=0)
    WikiPage: str = "www.wikipedia.com"

    def __lt__(self, obj):
        if type(obj) == Media:
            return (
                self.MediaType < obj.MediaType
                if self.MediaType != obj.MediaType
                else self.Title < obj.Title
            )


def LoadFiles() -> list[Media]:
    pathList = []
    with open(os.path.join(django_settings.STATICFILES_DIRS[0], "mediaPaths.csv"), "r") as fp:
        pathList = fp.read().split(",")
    MediaList: list[Media] = []
    for path in pathList:
        existingMedia = [x.Title for x in MediaList]
        splitList = path.replace("\\", "/").split("/")
        elementType = splitList[1]
        mediaTitle = splitList[-1] if elementType != "TV Shows" else splitList[-3]
        if mediaTitle not in existingMedia:
            MediaList.append(
                Media(
                    Title=mediaTitle,
                    MediaType=elementType,
                    Tags=splitList[2:-1] if elementType != "TV Shows" else splitList[2:-3],
                    Seasons=set() if elementType != "TV Shows" else set([splitList[-2]]),
                    Creator="" if elementType not in ["Youtube", "Podcasts"] else splitList[2],
                )
            )
            print(MediaList[-1])
        else:
            matchedMedia = [x for x in MediaList if x.Title == mediaTitle][0]
            matchedMedia.Seasons.add(splitList[-2])
    return sorted(MediaList)  # type:ignore


def FindPaths(root) -> bool:
    pathList = glob.glob(pathname="./**/*", root_dir=root, recursive=True)
    # pathList = os.walk(root)
    print(pathList)
    pathList = [x for x in pathList if "." in x.replace("\\", "/").split("/")[-1]]
    print()
    print(pathList)
    with open(os.path.join(django_settings.STATICFILES_DIRS[0], "mediaPaths.csv"), "w") as fp:
        fp.write(",".join(pathList))
    return True


def PopulateObjs(mediaList) -> list[Any]:
    objList = []
    for media in mediaList:
        obj = None
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
        if obj:
            objList.append(obj)
    return objList


def UpdateFromFolder(folder) -> str:
    FindPaths(root=folder)
    media = LoadFiles()
    media = PopulateObjs(mediaList=media)
    return "\n".join([str(x) for x in media])
