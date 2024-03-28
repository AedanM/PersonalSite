import os
import sys
import urllib.request

from django.db import models
from django.utils import timezone
from PIL import Image
from wikipedia import wikipedia  # type:ignore


class Media(models.Model):
    Title = models.CharField(max_length=200)
    GenreTags = models.TextField()
    Downloaded = models.BooleanField(default=False)
    InfoPage = models.CharField(max_length=200)
    Logo = models.CharField(
        default="https://upload.wikimedia.org/wikipedia/commons/c/c9/Icon_Video.png", max_length=200
    )

    def __lt__(self, cmpObj) -> bool:
        return str(self) < str(cmpObj)

    def __str__(self) -> str:
        return f"{self.Title}"

    @property
    def GenreTagList(self) -> list:
        return [x.strip() for x in sorted(self.GenreTags.split(","))]

    def GetLogo(self) -> Image.Image | str:
        if not self.Logo or "http" in self.Logo or not os.path.exists(f"static/{self.Logo}"):
            if "wikipedia" in self.InfoPage:
                searchTitle = self.InfoPage.split("/wiki/")[-1]
                m = wikipedia.WikipediaPage(searchTitle)
                relevantPics = [
                    x for x in m.images if ".svg" not in x and ("title" in x or "logo" in x)
                ]
                if not relevantPics:
                    relevantPics = [x for x in m.images if ".svg" not in x]
            elif "http" in self.Logo:
                relevantPics = [self.Logo]
            else:
                relevantPics = [self.InfoPage]
            if relevantPics:
                urllib.request.urlretrieve(
                    relevantPics[0],
                    "temp.png",
                )
                img = Image.open("temp.png")
                imScale = 480 / img.size[0]
                newSize = round(img.size[0] * imScale), round(img.size[1] * imScale)
                img = img.resize(newSize)
                savePath = f"logos/{self.Title.replace(':','-')}.png"
                img.save(f"static/{savePath}")
                setattr(self, "Logo", savePath)
                self.save()

        return self.Logo


class WatchableMedia(Media):
    Watched = models.BooleanField(default=True)
    Duration = models.DurationField()


class TVShow(WatchableMedia):
    Length = models.IntegerField()

    def __str__(self) -> str:
        return (
            super().__str__()
            + f" Season{'s' if self.Length > 0 else ''}"
            + f" 1{'-' if self.Length > 0 else ''}{self.Length if self.Length > 0 else ''}"
        )


class Movie(WatchableMedia):
    Year = models.IntegerField()

    def __str__(self) -> str:
        return super().__str__() + f" ({self.Year})"


class Youtube(WatchableMedia):
    Creator = models.CharField(max_length=50)
    Link = models.CharField(max_length=200)

    def __str__(self) -> str:
        return f"{self.Creator} " + super().__str__()


class Book(WatchableMedia):
    Author = models.CharField(max_length=50)


class Podcast(WatchableMedia):
    Show = models.CharField(max_length=50)
