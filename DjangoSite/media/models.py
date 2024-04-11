import datetime
import os

from django.conf import settings as django_settings
from django.db import models

from .modules.Model_Tools import DEFAULT_IMG, DownloadImage


class Media(models.Model):
    Title: models.CharField = models.CharField(max_length=200)
    Genre_Tags: models.TextField = models.TextField()
    Downloaded: models.BooleanField = models.BooleanField(default=False)
    InfoPage: models.CharField = models.CharField(max_length=200)
    Logo: models.CharField = models.CharField(default=DEFAULT_IMG, max_length=200)
    Rating: models.IntegerField = models.IntegerField(default=0)

    def __lt__(self, cmpObj) -> bool:
        return self.sortTitle < cmpObj.sortTitle

    @property
    def sortTitle(self):
        return str(self.Title).replace("The", "").replace("A ", "").strip()

    def __str__(self) -> str:
        return f"{self.Title}"

    @property
    def GenreTagList(self) -> list:
        return [x.strip() for x in sorted(self.Genre_Tags.split(","))]

    def GetLogo(self, loadLogo) -> str:
        if loadLogo or not os.path.exists(
            os.path.join(django_settings.STATICFILES_DIRS[0], self.Logo)
        ):
            DownloadImage(self)
        if self.InfoPage == "http://127.0.0.1:8000/media":
            self.InfoPage = "http://127.0.0.1:8000/media"
            self.save()
        return self.Logo


class WatchableMedia(Media):
    Watched: models.BooleanField = models.BooleanField(default=True)
    Duration: models.DurationField = models.DurationField()


class TVShow(WatchableMedia):
    Length: models.IntegerField = models.IntegerField()

    def __str__(self) -> str:
        if not self.Length:
            self.Length = 999
            self.save()
        return (
            super().__str__()
            + f" Season{'s' if self.Length > 0 else ''}"
            + f" 1{'-' if self.Length > 0 else ''}{self.Length if self.Length > 0 else ''}"
        )


class Movie(WatchableMedia):
    Year: models.IntegerField = models.IntegerField()

    def __str__(self) -> str:
        if not self.Year:
            self.Year = 1900
            self.save()
        return super().__str__() + f" ({self.Year})"


class Youtube(WatchableMedia):
    Creator: models.CharField = models.CharField(max_length=50)
    Link: models.CharField = models.CharField(max_length=200)

    def __str__(self) -> str:
        if not self.Creator:
            self.Creator = "undef"
            self.save()
        return f"{self.Creator} " + super().__str__()


class Novel(Media):
    Author: models.CharField = models.CharField(max_length=50)
    PageLength: models.IntegerField = models.IntegerField(default=0)

    def __str__(self) -> str:
        if not self.Author:
            self.Author = "undef"
            self.save()
        return f"{self.Author} " + super().__str__()


class Comic(Media):
    Company: models.CharField = models.CharField(max_length=50)
    Character: models.CharField = models.CharField(max_length=50)
    PageLength: models.IntegerField = models.IntegerField(default=0)

    def __str__(self) -> str:
        if not self.Company:
            self.Company = "undef"
            self.save()
        if not self.Character:
            self.Character = "undef"
            self.save()
        return f"{self.Character} ({self.Company}) " + super().__str__()


class Podcast(WatchableMedia):
    Creator: models.CharField = models.CharField(max_length=50)

    def __str__(self) -> str:
        if not self.Creator:
            self.Creator = "undef"
            self.save()
        return f"{self.Creator} " + super().__str__()
