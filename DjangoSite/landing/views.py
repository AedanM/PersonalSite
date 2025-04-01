import os
import shutil
from pathlib import Path

import frontmatter
import markdown  # type:ignore
from django.conf import settings as django_settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from landing.modules.HardwareFunctions import KillRedirect, PullRepo, RebootPC


# Create your views here.
def Index(request) -> HttpResponse:
    context: dict = {"colorMode": request.COOKIES.get("colorMode", "dark")}
    return render(request, "landing/index.html", context)


def IterLink(request) -> HttpResponse:
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
def Refresh(request) -> KillRedirect:
    if request.GET.get("hard", "False") == "True":
        RebootPC()
    if request.GET.get("pull", "False") == "True":
        PullRepo()
    return KillRedirect(request.META.get("HTTP_REFERER", "/media"))


@login_required
def ToolsPage(request) -> HttpResponse:
    return render(
        request,
        "landing/tools.html",
        context={"colorMode": request.COOKIES.get("colorMode", "dark")},
    )


def BlogHome(request) -> HttpResponse:
    context: dict = {"colorMode": request.COOKIES.get("colorMode", "dark")}
    context["posts"] = [
        frontmatter.load(str(x)).to_dict()
        for x in (django_settings.SYNC_PATH / "blog").glob("*.md")
    ]
    context["posts"] = sorted(context["posts"], key=lambda x: str(x["last_update"]))
    if request.GET.get("tag", None):
        context["posts"] = [x for x in context["posts"] if request.GET["tag"] in x["tags"]]
    if not request.user.is_authenticated:
        context["posts"] = [x for x in context["posts"] if "internal" not in x["tags"]]  # type: ignore
    return render(request, "landing/blogHome.html", context=context)


def BlogPages(request, path) -> HttpResponse:
    context: dict = {"colorMode": request.COOKIES.get("colorMode", "dark")}
    response = redirect("/blog")

    expectedName = f"{path}.md"
    syncFile = (django_settings.SYNC_PATH / "blog") / expectedName
    localFile = (django_settings.STATIC_ROOT / "blog") / expectedName

    if syncFile.exists():
        if not localFile.exists() or os.path.getmtime(localFile) < os.path.getmtime(syncFile):
            localFile.parent.mkdir(exist_ok=True)
            (localFile.parent / "attachments").mkdir(exist_ok=True)
            shutil.copy(syncFile, localFile)
            shutil.copytree(
                syncFile.parent / "attachments",
                localFile.parent / "attachments",
                dirs_exist_ok=True,
            )

        fMatterObj = frontmatter.load(str(localFile))
        context["rendered"] = markdown.markdown(
            fMatterObj.content, extensions=["tables", "fenced_code"]
        )
        context |= fMatterObj.to_dict()
        response = render(request, "landing/blogBase.html", context=context)
    return response
