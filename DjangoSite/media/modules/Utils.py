import re
from typing import Any

from django.core.exceptions import ObjectDoesNotExist

# pylint: disable=E0402
from ..forms import AlbumForm, ComicForm, MovieForm, NovelForm, PodcastForm, TVForm, YoutubeForm
from ..models import Album, Comic, Movie, Novel, Podcast, TVShow, Youtube


def CamelToSentence(text: str) -> str:
    matches = re.finditer(".+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)", text)
    return " ".join([m.group(0) for m in matches])


def ModelDisplayName(model):
    return CamelToSentence(model.__name__ + "s")


def FormMatch(obj):
    form = MovieForm
    if isinstance(obj, Movie):
        form = MovieForm
    elif isinstance(obj, TVShow):
        form = TVForm
    elif isinstance(obj, Novel):
        form = NovelForm
    elif isinstance(obj, Comic):
        form = ComicForm
    elif isinstance(obj, Podcast):
        form = PodcastForm
    elif isinstance(obj, Youtube):
        form = YoutubeForm
    elif isinstance(obj, Album):
        form = AlbumForm
    return form


def DetermineForm(request):
    contentType = "Movie"
    if "Year" in request.POST:
        pass
    elif "Length" in request.POST:
        contentType = "TV"
    elif "Creator" in request.POST:
        if "Link" in request.POST:
            contentType = "Youtube"
        else:
            contentType = "Podcast"
    elif "Author" in request.POST:
        contentType = "Book"
    elif "Character" in request.POST:
        contentType = "Comic"
    elif "Artist" in request.POST:
        contentType = "Album"
    return GetFormAndClass(contentType)


def GetFormAndClass(formType) -> tuple:
    cls: Any = MovieForm
    obj: Any = Movie
    if "Movie" in formType:
        cls = MovieForm
        obj = Movie
    elif "TV" in formType:
        cls = TVForm
        obj = TVShow
    elif "Book" in formType:
        cls = NovelForm
        obj = Novel
    elif "Comic" in formType:
        cls = ComicForm
        obj = Comic
    elif "Podcast" in formType:
        cls = PodcastForm
        obj = Podcast
    elif "Youtube" in formType:
        cls = YoutubeForm
        obj = Youtube
    elif "Album" in formType:
        cls = AlbumForm
        obj = Album
    return cls, obj


MODEL_LIST = [Movie, TVShow, Novel, Comic, Podcast, Youtube, Album]


def ContentFilter(getParams: dict, contentList) -> list:
    returnList = contentList
    if "genre" in getParams:
        returnList = [x for x in returnList if getParams["genre"] in x.GenreTagList]
    return sorted(returnList)


def GetContents(request) -> dict[str, dict]:
    # pylint: disable=E1101
    loadLogo = "updateLogos" in request.GET
    outDict = {}
    for model in MODEL_LIST:
        modelList = ContentFilter(request.GET, model.objects.all())
        outDict[ModelDisplayName(model)] = dict(
            zip(modelList, [x.GetLogo(loadLogo) for x in modelList])
        )
    return outDict


def FindID(contentID: str) -> Any:
    for model in MODEL_LIST:
        try:
            # pylint: disable=E1101
            obj = model.objects.get(pk=contentID)
        except ObjectDoesNotExist:
            obj = None
        if obj:
            return obj
    return None


def GetAllTags(objType=None) -> dict[str, int]:
    genres = []
    genreFreq = {}
    modelTypes = [objType] if objType else MODEL_LIST
    _ = [
        [[genres.append(y) for y in x.GenreTagList] for x in modelType.objects.all()]
        for modelType in modelTypes
    ]
    for i in set(genres):
        genreFreq[i] = genres.count(i)
    return dict(sorted(genreFreq.items(), key=lambda x: x[1], reverse=True))
