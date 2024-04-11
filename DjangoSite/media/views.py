import sys

from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from django import forms
from django.db import models
from typing import Any
from .modules.UpdateFromFolder import UpdateFromFolder
from .modules.Web_Tools import GetShowInfo
from .modules.DB_Tools import CleanDupes
from .models import Comic, Novel, Movie, Podcast, TVShow, Youtube
from .forms import ComicForm, NovelForm, MovieForm, PodcastForm, TVForm, YoutubeForm

# Create your views here.


def ContentFilter(getParams: dict, contentList) -> list:
    returnList = contentList
    if "genre" in getParams:
        returnList = [x for x in returnList if getParams["genre"] in x.GenreTagList]
    return sorted(returnList)


def GetContents(request) -> dict[str, dict]:
    loadLogo = "loadLogos" in request.GET
    MovieList = ContentFilter(request.GET, Movie.objects.all())
    TVList = ContentFilter(request.GET, TVShow.objects.all())
    YoutubeList = ContentFilter(request.GET, Youtube.objects.all())
    PodcastList = ContentFilter(request.GET, Podcast.objects.all())
    ComicList = ContentFilter(request.GET, Comic.objects.all())
    NovelList = ContentFilter(request.GET, Novel.objects.all())
    return {
        "Movies": dict(zip(MovieList, [x.GetLogo(loadLogo) for x in MovieList])),
        "TV Shows": dict(zip(TVList, [x.GetLogo(loadLogo) for x in TVList])),
        "Youtube": dict(zip(YoutubeList, [x.GetLogo(loadLogo) for x in YoutubeList])),
        "Podcasts": dict(zip(PodcastList, [x.GetLogo(loadLogo) for x in PodcastList])),
        "Books": dict(zip(NovelList, [x.GetLogo(loadLogo) for x in NovelList])),
        "Comics": dict(zip(ComicList, [x.GetLogo(loadLogo) for x in ComicList])),
    }


def index(request) -> HttpResponse:
    soloContent = request.GET["type"] if "type" in request.GET else None
    context = {
        "MediaTypes": (
            GetContents(request=request)
            if soloContent == None
            else GetContents(request=request)[soloContent]
        ),
        "Graphs": "noGraphs" in request.GET,
    }
    return render(request, "media/newIndex.html", context)


def update(request) -> HttpResponse:
    if "clean" not in request.GET:
        response = UpdateFromFolder(
            folder=r"W:/", useFile="useFile" in request.GET, save="save" in request.GET
        )
    else:
        _, model = GetFormAndClass(request=request)
        response = CleanDupes(model=model)  # type:ignore
    return HttpResponse(content=response, content_type="text/plain")


def wikiScrape(request) -> HttpResponse:
    response = GetShowInfo(wikiLink=request.GET["show"] if "show" in request.GET else False)
    return HttpResponse(content=response, content_type="text/json")


def new(request) -> HttpResponse:
    response: HttpResponse = redirect("/media")
    if "type" in request.GET:
        cls, obj = GetFormAndClass(request)

        inst = obj.objects.get(id=request.GET["instance"]) if "instance" in request.GET else None

        form = cls(request.POST or None, instance=inst)
        if form.is_valid():
            form.save()
        context = {}
        context["form"] = form
        response = (
            render(request, "media/form.html", context)
            if request.method == "GET"
            else redirect("/media")
        )

    return response


def GetFormAndClass(request) -> tuple:
    formType = request.GET["type"]
    cls: Any = MovieForm
    obj: Any = Movie
    if "Movie" in formType:
        cls = MovieForm
        obj = Movie
    elif "TV" in formType:
        cls = TVForm
        obj = TVShow
    elif "Novel" in formType:
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
    return cls, obj
