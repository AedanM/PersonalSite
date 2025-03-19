from pathlib import Path

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from landing.modules.HardwareFunctions import KillRedirect, PullRepo, RebootPC


# Create your views here.
def index(request) -> HttpResponse:
    context: dict = {"colorMode": request.COOKIES.get("colorMode", "dark")}
    return render(request, "landing/index.html", context)


def iterLink(request):
    link = request.GET.get("link")
    start = int(request.GET.get("start", 0))
    pad = int(request.GET.get("pad", 0))
    end = int(request.GET.get("end", 10)) + 1
    linkList = [
        link.replace("{idx}", "{number:0{width}d}".format(width=pad, number=x))
        for x in range(start, end)
    ]
    context: dict = {"colorMode": request.COOKIES.get("colorMode", "dark"), "linkList": linkList}
    return render(request, "landing/iterLink.html", context)


def Log(request):
    extendLogPath = sorted(list(Path(r".\Logging").glob("*Extended.log")))[-1]
    userLogPath = sorted(list(Path(r".\Logging").glob("*UserLogger.log")))[-1]

    r = (
        extendLogPath.read_text(newline="\n")
        if request.GET.get("full", "False") == "True"
        else userLogPath.read_text(newline="\n")
    )

    return HttpResponse(r, content_type="text/plain")


@login_required
def refresh(request):
    if request.GET.get("hard", "False") == "True":
        RebootPC()
    if request.GET.get("pull", "False") == "True":
        PullRepo()
    return KillRedirect(request.META.get("HTTP_REFERER", "/media"))


@login_required
def tools(request):
    return render(
        request,
        "landing/tools.html",
        context={"colorMode": request.COOKIES.get("colorMode", "dark")},
    )
