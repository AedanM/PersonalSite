import datetime
from django.db import models
from .modules.DownloadImage import DownloadImage


class Media(models.Model):
    Title = models.CharField(max_length=200)
    Genre_Tags = models.TextField()
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
        return [x.strip() for x in sorted(self.Genre_Tags.split(","))]

    def GetLogo(self, loadLogo) -> str:
        if loadLogo:
            DownloadImage(self)
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


class Novel(Media):
    Author = models.CharField(max_length=50)
    PageLength = models.IntegerField(default=0)

    def __str__(self) -> str:
        return f"{self.Author} " + super().__str__()


class Comic(Media):
    Company = models.CharField(max_length=50)
    Character = models.CharField(max_length=50)
    PageLength = models.IntegerField(default=0)

    def __str__(self) -> str:
        return f"{self.Character} ({self.Company}) " + super().__str__()


class Podcast(WatchableMedia):
    Creator = models.CharField(max_length=50)

    def __str__(self) -> str:
        return f"{self.Creator} " + super().__str__()
