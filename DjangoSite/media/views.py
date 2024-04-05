import sys
from urllib import response

from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect

from .modules.UpdateFromFolder import UpdateFromFolder
from .modules.GetWikiInfo import GetShowInfo
from .models import Comic, Novel, Movie, Podcast, TVShow, Youtube
from .forms import ComicForm, NovelForm, MovieForm, PodcastForm, TVForm, YoutubeForm

# Create your views here.


def ContentFilter(getParams: dict, movieList) -> list:
    returnList = movieList
    if "genre" in getParams:
        returnList = [x for x in returnList if getParams["genre"] in x.GenreTagList]
        print(getParams["genre"])
    return sorted(returnList)


def index(request) -> HttpResponse:
    MovieList = ContentFilter(request.GET, Movie.objects.all())
    TVList = ContentFilter(request.GET, TVShow.objects.all())
    YoutubeList = ContentFilter(request.GET, Youtube.objects.all())
    PodcastList = ContentFilter(request.GET, Podcast.objects.all())
    ComicList = ContentFilter(request.GET, Comic.objects.all())
    NovelList = ContentFilter(request.GET, Novel.objects.all())
    loadLogo = "loadLogos" in request.GET
    context = {
        "MediaTypes": {
            "Movies": dict(zip([x.GetLogo(loadLogo) for x in MovieList], MovieList)),
            "TV Shows": dict(zip([x.GetLogo(loadLogo) for x in TVList], TVList)),
            "Youtube": dict(zip([x.GetLogo(loadLogo) for x in YoutubeList], YoutubeList)),
            "Podcasts": dict(zip([x.GetLogo(loadLogo) for x in PodcastList], PodcastList)),
            "Books": dict(zip([x.GetLogo(loadLogo) for x in NovelList], NovelList)),
            "Comics": dict(zip([x.GetLogo(loadLogo) for x in ComicList], ComicList)),
        },
        "Graphs": "noGraphs" in request.GET,
    }
    return render(request, "media/newIndex.html", context)


def update(request) -> HttpResponse:
    response = UpdateFromFolder(
        folder=r"W:/", useFile="useFile" in request.GET, save="save" in request.GET
    )
    return HttpResponse(content=response, content_type="text/plain")


def wikiScrape(request) -> HttpResponse:
    response = GetShowInfo(wikiLink=request.GET["show"] if "show" in request.GET else False)
    return HttpResponse(content=response, content_type="text/json")


def new(request) -> HttpResponse:
    response = redirect("/media")
    if "type" in request.GET:
        formType = request.GET["type"]
        cls = MovieForm
        obj = Movie
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
