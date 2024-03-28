import sys

from django.http import HttpResponse
from django.shortcuts import render

from .models import Book, Movie, Podcast, TVShow, Youtube

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
    context = {
        "Movies": dict(zip([x.GetLogo() for x in MovieList], MovieList)),
        "TVShows": dict(zip([x.GetLogo() for x in TVList], TVList)),
        "YoutubeVids": dict(zip([x.GetLogo() for x in YoutubeList], YoutubeList)),
    }
    if "genre" in request.GET:
        pass
    return render(request, "media/index.html", context)
