# pylint: disable=C0103
import datetime
import logging
import urllib.error
from pathlib import Path

from django.conf import settings as django_settings
from django.db import models

from .modules.ModelTools import DEFAULT_IMG_PATH, DownloadImage
from .utils import MINIMUM_YEAR

LOGGER = logging.getLogger("UserLogger")


class Media(models.Model):
    Title: models.CharField = models.CharField(max_length=200)
    Genre_Tags: models.CharField = models.CharField(max_length=200)
    Logo: models.CharField = models.CharField(default=DEFAULT_IMG_PATH, max_length=200)
    InfoPage: models.CharField = models.CharField(max_length=200)
    Downloaded: models.BooleanField = models.BooleanField(default=False)
    Rating: models.DecimalField = models.DecimalField(
        default=0,  # type: ignore
        decimal_places=1,
        max_digits=3,
    )  # type: ignore

    def __lt__(self, cmpObj) -> bool:
        return self.SortTitle < cmpObj.SortTitle

    def delete(self, using=None, keep_parents=None):
        print(f"Deleting {self.Logo}")
        logoDst = Path(django_settings.STATICFILES_DIRS[0]) / self.Logo
        if logoDst.exists():
            logoDst.resolve().unlink()
        return super().delete(using, keep_parents)

    @property
    def SortTitle(self):
        return str(self.Title).replace("The ", "").replace("A ", "").strip()

    def __str__(self) -> str:
        return f"{self.Title}"

    @property
    def GenreTagList(self) -> list:
        return sorted([x.strip() for x in str(self.Genre_Tags).split(",")])

    def GetLogo(self, loadLogo) -> str:
        returnVal = DEFAULT_IMG_PATH
        if self.Logo == "None Found":
            self.Logo = returnVal
            self.save()
        try:
            logoDst = Path(django_settings.STATICFILES_DIRS[0]) / self.Logo
            if (loadLogo or not logoDst.exists()) and DownloadImage(self):
                returnVal = self.Logo
            else:
                LOGGER.error("No Logo Found at %s", self.Logo)
        except urllib.error.HTTPError as e:
            LOGGER.error("Logo Collection Failed %s", str(e))
        return returnVal

    @property
    def JsonRepr(self):
        outDict = {}
        for key, item in self.__dict__.items():
            if str(key[0]).isupper():
                if isinstance(item, datetime.timedelta):
                    item = int(item.seconds / 60)
                outDict[key.replace('"', "")] = item
        return outDict

    @property
    def BiggestTag(self) -> str:
        bigList = [
            "Sci-Fi",
            "Dimension 20",
            "Romance",
            "Educational",
            "Superheroes",
            "Mystery",
            "Comedy",
            "Drama",
            "Action",
        ]
        outVal = self.GenreTagList[0]
        for i in bigList:
            if i in self.GenreTagList:
                outVal = i
                break
        return outVal


class WatchableMedia(Media):
    Watched: models.BooleanField = models.BooleanField(default=False)
    Duration: models.DurationField = models.DurationField()


class TVShow(WatchableMedia):
    Length: models.IntegerField = models.IntegerField()
    Series_Start: models.DateField = models.DateField()
    Series_End: models.DateField = models.DateField()

    @property
    def Year(self):
        # pylint: disable=E1101
        return self.Series_Start.year

    @property
    def Total_Length(self):
        # pylint: disable=E1101
        return (self.Duration.seconds * self.Length) / 3600

    def __str__(self) -> str:
        # pylint: disable=E1101
        end_year = self.Series_End.year if self.Series_End else MINIMUM_YEAR
        endValue = end_year if end_year > MINIMUM_YEAR else "now"
        startValue = self.Series_Start.year if self.Series_Start else -1
        return super().__str__() + f" ({startValue}) - ({endValue})"


class Movie(WatchableMedia):
    Year: models.IntegerField = models.IntegerField()

    def __str__(self) -> str:
        if not self.Year:
            self.Year = MINIMUM_YEAR
            self.save()
        return super().__str__() + f" ({self.Year})"


class Youtube(WatchableMedia):
    Creator: models.CharField = models.CharField(max_length=50)
    Link: models.CharField = models.CharField(max_length=200)

    def __str__(self) -> str:
        return f"{self.Creator} " + super().__str__()


class Novel(Media):
    Author: models.CharField = models.CharField(max_length=50)
    PageLength: models.IntegerField = models.IntegerField(default=0)
    Read: models.BooleanField = models.BooleanField(default=False)

    @property
    def GenreTagList(self) -> list:
        tagList = super().GenreTagList
        if self.Author not in tagList:
            tagList.append(self.Author)
        return tagList

    def __str__(self) -> str:
        return f"{self.Author} " + super().__str__()


class Comic(Media):
    Company: models.CharField = models.CharField(max_length=50)
    Character: models.CharField = models.CharField(max_length=50)
    PageLength: models.IntegerField = models.IntegerField(default=0)
    Read: models.BooleanField = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.Character} ({self.Company}) " + super().__str__()


class Podcast(WatchableMedia):
    Creator: models.CharField = models.CharField(max_length=50)

    def __str__(self) -> str:
        return f"{self.Creator} " + super().__str__()


class Album(WatchableMedia):
    Artist: models.CharField = models.CharField(max_length=75)
    Year: models.IntegerField = models.IntegerField(default=-1)

    def __str__(self) -> str:
        return f"{self.Artist}'s {self.Title} {self.Year}"
