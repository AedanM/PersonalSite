import os

from django.http import HttpResponse
from django.shortcuts import render
from media.models import Movie, TVShow


# Create your views here.
def index(request) -> HttpResponse:
    context = {"Movies": Movie.objects.all(), "TV Shows": TVShow.objects.all()}
    return render(request, "landing/index.html", context)
