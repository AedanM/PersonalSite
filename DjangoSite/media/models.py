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

    def __str__(self) -> str:
        return f"{self.Title}"

    def GetLogo(self, webTitle: str = "") -> Image.Image:
        searchTitle = self.Title
        if webTitle:
            searchTitle = webTitle
        m = wikipedia.WikipediaPage(searchTitle)

        relevantPics = [x for x in m.images if self.Title in x]
        print(relevantPics[0])
        urllib.request.urlretrieve(
            relevantPics[0],
            "logo.png",
        )
        img = Image.open("logo.png")
        return img


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
