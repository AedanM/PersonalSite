from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.


def resume(request) -> HttpResponse:
    context: dict = {}
    return render(request, "resume/resume.html", context)
