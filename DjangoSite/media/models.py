# pylint: disable=C0103
import datetime
import os

from django.conf import settings as django_settings
from django.db import models

from .modules.ModelTools import DEFAULT_IMG, DEFAULT_IMG_PATH, DownloadImage
from .utils import MINIMUM_YEAR


class Media(models.Model):
    Title: models.CharField = models.CharField(max_length=200)
    Genre_Tags: models.TextField = models.TextField()
    Downloaded: models.BooleanField = models.BooleanField(default=False)
    InfoPage: models.CharField = models.CharField(max_length=200)
    Logo: models.CharField = models.CharField(default=DEFAULT_IMG, max_length=200)
    Rating: models.DecimalField = models.DecimalField(default=0, decimal_places=1, max_digits=3)  # type: ignore

    def __lt__(self, cmpObj) -> bool:
        return self.SortTitle < cmpObj.SortTitle

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
        logoExists = os.path.exists(os.path.join(django_settings.STATICFILES_DIRS[0], self.Logo))
        if loadLogo and not logoExists or not logoExists:
            DownloadImage(self)
        logoExists = os.path.exists(os.path.join(django_settings.STATICFILES_DIRS[0], self.Logo))
        if logoExists:
            returnVal = self.Logo
        else:
            print("No Logo")
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
        return self.Duration * self.Length

    def __str__(self) -> str:
        # pylint: disable=E1101
        end_year = self.Series_End.year if self.Series_End else MINIMUM_YEAR
        return (
            super().__str__()
            + f" ({self.Series_Start.year if self.Series_Start else -1}) - ({end_year if end_year > MINIMUM_YEAR else 'now'})"
        )


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
