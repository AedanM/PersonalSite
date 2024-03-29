import sys

from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import render

from .models import Book, Movie, Podcast, TVShow, Youtube
from .forms import BookForm, MovieForm, PodcastForm, TVForm, YoutubeForm

# Create your views here.


def ContentFilter(getParams: dict, movieList) -> list:
    returnList = movieList
    if "genre" in getParams:
        returnList = [x for x in returnList if getParams["genre"] in x.GenreTagList]
    return sorted(returnList)


def index(request) -> HttpResponse:
    MovieList = ContentFilter(request.GET, Movie.objects.all())
    TVList = ContentFilter(request.GET, TVShow.objects.all())
    YoutubeList = ContentFilter(request.GET, Youtube.objects.all())
    PodcastList = ContentFilter(request.GET, Podcast.objects.all())
    context = {
        "Movies": dict(zip([x.GetLogo() for x in MovieList], MovieList)),
        "TVShows": dict(zip([x.GetLogo() for x in TVList], TVList)),
        "YoutubeVids": dict(zip([x.GetLogo() for x in YoutubeList], YoutubeList)),
        "Podcasts": dict(zip([x.GetLogo() for x in PodcastList], PodcastList)),
    }
    if "genre" in request.GET:
        pass
    return render(request, "media/index.html", context)


def update(request) -> HttpResponse:
    response = Movie.FindElements(TVShow)
    return HttpResponse(response, content_type="text/plain")


def new(request) -> HttpResponse:

    if "type" in request.GET:
        formType = request.GET["type"]
        cls = MovieForm
        if "Movie" in formType:
            cls = MovieForm
        elif "TV" in formType:
            cls = TVForm
        elif "Book" in formType:
            cls = BookForm
        elif "Podcast" in formType:
            cls = PodcastForm
        elif "Youtube" in formType:
            cls = YoutubeForm

        form = cls(request.POST or None, request.FILES or None)

        if form.is_valid():
            form.save()
        context = {}
        context["form"] = form
        print(request.GET)
        return render(request, "media/form.html", context)
    else:
        return index(request)
