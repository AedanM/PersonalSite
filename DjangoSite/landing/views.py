"""Landing views."""

import shutil
from pathlib import Path

import frontmatter
import markdown
from django.conf import settings as django_settings
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from landing.modules.HardwareFunctions import KillRedirect, PullRepo


# Create your views here.
def Index(request: HttpRequest) -> HttpResponse:
    """Index of landing."""
    context: dict = {"colorMode": request.COOKIES.get("colorMode", "dark")}
    return render(request, "landing/index.html", context)


def IterLink(request: HttpRequest) -> HttpResponse:
    """Automatically iterate a link with {idx}."""
    link = request.GET.get("link", "")
    start = int(request.GET.get("start", 0))
    pad = int(request.GET.get("pad", 0))
    end = int(request.GET.get("end", 10)) + 1
    step = int(request.GET.get("step", 1))
    linkList = [
        link.replace("{idx}", "{number:0{width}d}".format(width=pad, number=x))
        for x in range(start, end, step)
    ]
    context: dict = {"colorMode": request.COOKIES.get("colorMode", "dark"), "linkList": linkList}
    return render(request, "landing/iterLink.html", context)


def Log(request: HttpRequest) -> HttpResponse:
    """Return current log file."""
    extendLogPath = sorted(Path(r".\Logging").glob("*Extended.log"))[-1]
    userLogPath = sorted(Path(r".\Logging").glob("*UserLogger.log"))[-1]

    r = (
        extendLogPath.read_text(newline="\n")
        if request.GET.get("full", "False") == "True"
        else userLogPath.read_text(newline="\n")
    )

    return HttpResponse(r, content_type="text/plain")


def Refresh(request: HttpRequest) -> KillRedirect:
    """Refresh process."""
    if request.GET.get("pull", "False") == "True":
        PullRepo()
    return KillRedirect(request.META.get("HTTP_REFERER", "/media"))


@login_required
def ToolsPage(request: HttpRequest) -> HttpResponse:
    """Load page of useful tools."""
    return render(
        request,
        "landing/tools.html",
        context={"colorMode": request.COOKIES.get("colorMode", "dark")},
    )


def BlogHome(request: HttpRequest) -> HttpResponse:
    """Load blog home page."""
    context: dict = {"colorMode": request.COOKIES.get("colorMode", "dark")}
    postParent = django_settings.SYNC_PATH / "blog" / "posts"
    context["posts"] = [
        frontmatter.load(str(x)).to_dict() | {"path": x}
        for x in postParent.glob("**/*.md")
        if x.parent.name[0] not in ["_", "."]
    ]
    for p in context["posts"]:
        if p["path"].parent != postParent and isinstance(p.get("tags", None), list):
            p["tags"].append(p["path"].parent.name)

    context["posts"] = sorted(context["posts"], key=lambda x: str(x["creation_date"]), reverse=True)
    if request.GET.get("tag", None):
        context["posts"] = [x for x in context["posts"] if request.GET["tag"] in x["tags"]]
    if not request.user.is_authenticated:
        context["posts"] = [x for x in context["posts"] if "internal" not in x["tags"]]
    return render(request, "landing/blogHome.html", context=context)


def BlogPages(request: HttpRequest, path: str, parent: str | None = None) -> HttpResponse:
    """Load individual blog pages."""
    context: dict = {"colorMode": request.COOKIES.get("colorMode", "dark")}
    response = redirect("/blog")
    expectedName = f"{path}.md" if parent is None else f"{parent}/{path}.md"
    syncFile = (django_settings.SYNC_PATH / "blog" / "posts") / expectedName
    localFile = (django_settings.STATIC_ROOT / "blog" / "posts") / expectedName

    if syncFile.exists():
        if (
            not localFile.exists()
            or Path(localFile).stat().st_mtime < Path(syncFile).stat().st_mtime
        ):
            localFile.parent.mkdir(exist_ok=True)
            (localFile.parent / "attachments").mkdir(exist_ok=True)
            shutil.copy(syncFile, localFile)
            shutil.copytree(
                django_settings.SYNC_PATH / "blog" / "attachments",
                django_settings.STATIC_ROOT / "blog" / "attachments",
                dirs_exist_ok=True,
            )

        fMatterObj = frontmatter.load(str(localFile))
        context["rendered"] = markdown.markdown(
            fMatterObj.content,
            extensions=["tables", "fenced_code"],
        )
        context |= fMatterObj.to_dict()
        if parent:
            context["tags"].append(parent)
        context["tags"] = sorted(context["tags"])
        response = render(request, "landing/blogBase.html", context=context)
    return response
