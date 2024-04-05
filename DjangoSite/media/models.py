import os
from pprint import pp
import urllib.request
import datetime
from django.db import models
from PIL import Image
from wikipedia import wikipedia  # type:ignore

from django.conf import settings as django_settings


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

    def GetLogo(self) -> Image.Image | str:
        relevantPics = None
        if (
            not self.Logo
            or "http" in self.Logo
            or not os.path.exists(os.path.join(django_settings.STATIC_ROOT, f"{self.Logo}"))
        ):
            if "http" in self.Logo and "@" not in self.Logo:
                relevantPics = [self.Logo]
            elif "wikipedia" in self.InfoPage:
                try:
                    searchTitle = self.InfoPage.split("/wiki/")[-1]
                    m = wikipedia.WikipediaPage(searchTitle)  # type:ignore
                    relevantPics = [
                        x for x in m.images if ".svg" not in x and ("title" in x or "logo" in x)
                    ]
                    if not relevantPics:
                        relevantPics = [x for x in m.images if ".svg" not in x]
                except:
                    pass
            else:
                relevantPics = [self.InfoPage]
            if relevantPics:
                try:
                    urllib.request.urlretrieve(
                        relevantPics[0],
                        "temp.png",
                    )
                    img = Image.open("temp.png")
                    imScale = 480 / img.size[0]
                    newSize = round(img.size[0] * imScale), round(img.size[1] * imScale)
                    img = img.resize(newSize)
                    savePath = f"logos/{self.Title.replace(':','-')}.png"
                    localPath = os.path.join(django_settings.STATICFILES_DIRS[0], f"{savePath}")
                    img.save(localPath)
                    os.remove("temp.png")
                    setattr(self, "Logo", savePath)
                    self.save()
                except ConnectionError:
                    pass

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
    Creator = models.CharField(max_length=50)


MediaServerNameMap = {
    Movie: "Movies",
    TVShow: "TV Shows",
    Youtube: "Youtube",
    Podcast: "Podcasts",
    Book: "Books",
}


def GenerateTVShows(TVList):
    for s in TVList[0]:
        if type(s) == list:
            title = s[0]
            seasonCount = len(s) - 1
            if not (TVShow.objects.filter(Title__contains=title)):
                t = TVShow(
                    Length=seasonCount,
                    Title=title,
                    GenreTags="",
                    Downloaded=True,
                    Watched=False,
                    InfoPage="None",
                    Duration=datetime.timedelta(hours=1),
                )
                t.save()
