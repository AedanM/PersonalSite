import sys
import urllib.request

from django.db import models
from django.utils import timezone
from PIL import Image
from wikipedia import wikipedia  # type:ignore


# Create your models here.
class WatchableMedia(models.Model):
    Title = models.CharField(max_length=200)
    GenreTags = models.TextField()
    Downloaded = models.BooleanField(default=False)
    Watched = models.BooleanField(default=True)
    ImportDate = models.DateTimeField(default=timezone.now)
    AddedBy = models.CharField(max_length=200)
    WikiPage = models.CharField(max_length=200)

    def __lt__(self, cmpObj) -> bool:
        return str(self) < str(cmpObj)

    def __str__(self) -> str:
        return f"{self.Title}"

    @property
    def GenreTagList(self) -> list:
        return [x.strip() for x in sorted(self.GenreTags.split(","))]

    def GetLogo(self) -> Image.Image | str:
        searchTitle = self.WikiPage.split("/wiki/")[-1]
        m = wikipedia.WikipediaPage(searchTitle)
        print(m.images, file=sys.stderr)
        relevantPics = [x for x in m.images if ".svg" not in x]
        return (
            relevantPics[0]
            if relevantPics
            else "https://upload.wikimedia.org/wikipedia/commons/c/c9/Icon_Video.png"
        )
        # print(relevantPics[0])
        # urllib.request.urlretrieve(
        # relevantPics[0],
        # "logo.png",
        # )
        # img = Image.open("logo.png")
        # return img


class TVShow(WatchableMedia):
    Length = models.IntegerField()
    Progress = models.IntegerField()

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
