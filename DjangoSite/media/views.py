import sys

from django.http import HttpResponse
from django.shortcuts import render

from .models import Movie, TVShow

# Create your views here.


def ContentFilter(getParams: dict, movieList) -> list:
    returnList = movieList
    if "genre" in getParams:
        returnList = [x for x in returnList if getParams["genre"] in x.GenreTagList]
    return sorted(returnList)


def index(request) -> HttpResponse:
    MovieList = ContentFilter(request.GET, Movie.objects.all())
    TVList = ContentFilter(request.GET, TVShow.objects.all())
    context = {
        "Movies": dict(zip([x.GetLogo() for x in MovieList], MovieList)),
        "TVShows": dict(zip([x.GetLogo() for x in TVList], TVList)),
    }
    if "genre" in request.GET:
        pass
    return render(request, "media/index.html", context)
