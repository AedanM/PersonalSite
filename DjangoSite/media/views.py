# pylint: disable=C0103
import logging
import time

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse, HttpResponseNotFound
from django.shortcuts import redirect, render

from .models import Movie, TVShow
from .modules.CheckDetails import CheckMovies, CheckTV
from .modules.ModelTools import DownloadImage, SortTags
from .modules.Utils import (
    MODEL_LIST,
    DetermineForm,
    FilterMedia,
    FindID,
    FormMatch,
    GetFormAndClass,
)
from .modules.WikiParse import ScrapeWiki

# Create your views here.
LOGGER = logging.getLogger("UserLogger")
DEFAULT_SORT_TERMS: list[str] = ["Random", "Date Added"]


def apiRedirect(_request) -> HttpResponse:
    return redirect("/media/api/docs")


def viewMedia(request) -> HttpResponse:
    context = {"object": FindID(request.GET.get("id", -1))}
    context["colorMode"] = request.COOKIES.get("colorMode", "dark")

    return render(request, "media/mediaPage.html", context)


@login_required
def delete(request) -> HttpResponse:
    confirm = request.GET.get("confirm", "False")
    if contentObj := FindID(request.GET.get("id", -1)):
        if confirm == "True":
            contentObj.delete()
        else:
            return render(
                request,
                "media/confirmPage.html",
                context={
                    "inst": contentObj,
                    "src": f"/media/delete?id={contentObj.id}",
                    "colorMode": request.COOKIES.get("colorMode", "dark"),
                },
            )
    else:
        return HttpResponseNotFound("No Matching ID Found")
    return redirect("/media")


@login_required
def wikiLoad(request) -> HttpResponse:
    context = {}
    context["link"] = request.GET.get("link", None)
    returnRender = render(request, "media/wikiLoad.html", context=context)
    form, _model = GetFormAndClass(request.POST.get("Type", "Movie"))
    if request.method == "POST":
        input_value = request.POST.get("Wiki Link", None)
        if input_value:
            contentDetails = ScrapeWiki(wikiLink=input_value)
            context["form"] = form(initial=contentDetails)
            for key in context["form"].fields:
                if (
                    key not in ["Downloaded", "Rating", "Genre_Tags", "Watched"]
                    and key not in contentDetails
                ):
                    context["wikiLink"] = input_value
                    break
            context["colorMode"] = request.COOKIES.get("colorMode", "dark")
            returnRender = render(request, "media/form.html", context=context)
        else:
            form, model = DetermineForm(request)
            activeForm = form(request.POST)
            # pylint: disable=E1101
            matchingObjs = [
                x
                for x in model.objects.all()
                if x.InfoPage == activeForm.data["InfoPage"] and x.Title == activeForm.data["Title"]
            ]
            if activeForm.is_valid() and len(matchingObjs) == 0:

                activeForm.save()
                # pylint: disable=E1101
                obj = model.objects.filter(Title=request.POST.get("Title")).first()
                if obj:
                    SortTags(obj)
                    DownloadImage(obj)
                    obj.GetLogo(True)
                    LOGGER.info("Loaded %s from Wikipedia", obj.Title)
                    returnRender = redirect("/media")
                else:
                    LOGGER.error("Wiki load failed from %s", activeForm.data["InfoPage"])
            else:
                LOGGER.warning("Matching Object Found for %s, Not Added", activeForm.data["Title"])
            returnRender = redirect(f"/media/{model.__name__}s?sort=Date+Added")
    return returnRender


@login_required
def adjustTags(_request, fromTag: str, toTag: str):

    # pylint: disable=E1101
    for media in MODEL_LIST:
        for m in media.objects.all():
            m.Genre_Tags = m.Genre_Tags.replace(fromTag, toTag)
            m.save()
    return redirect("/media")


@login_required
def checkFiles(request) -> HttpResponse:
    unmatchedTV, matchedTV = CheckTV()
    unmatchedMovie, matchedMovie = CheckMovies()

    # pylint: disable=E1101
    wronglyMarkedMovie = [
        x
        for x in Movie.objects.all()
        if x.Downloaded and x.id not in [y["Match"]["ID"] for y in matchedMovie]  # type:ignore
    ]
    wronglyMarkedTV = [
        x
        for x in TVShow.objects.all()
        if x.Downloaded and x.id not in [y["Match"]["ID"] for y in matchedTV]  # type:ignore
    ]
    return render(
        request=request,
        template_name="media/checkFile.html",
        context={
            "tvshows": {
                "matched": matchedTV,
                "unmatched": unmatchedTV,
                "wronglyMarked": wronglyMarkedTV,
            },
            "movies": {
                "unmatched": unmatchedMovie,
                "matched": matchedMovie,
                "wronglyMarked": wronglyMarkedMovie,
            },
            "colorMode": request.COOKIES.get("colorMode", "dark"),
        },
    )


def stats(request) -> HttpResponse:
    start = time.time()
    context = {}
    for media in MODEL_LIST:
        # pylint: disable=E1101
        context[media.__name__] = media.objects.all()
    context["colorMode"] = request.COOKIES.get("colorMode", "dark")
    context["force"] = request.GET.get("force", "False") == "True"
    response = render(request, "media/stats.html", context=context)
    LOGGER.info("Stats Rendering Took %2.4f", time.time() - start)
    return response


@login_required
def new(request) -> HttpResponse:
    context = {}
    context["colorMode"] = request.COOKIES.get("colorMode", "dark")
    response: HttpResponse = render(request, "media/mediaChoice.html", context)

    if request.GET.get("type", None):
        cls, obj = GetFormAndClass(request.GET.get("type", "Movie"))

        # pylint: disable=E1101
        inst = obj.objects.get(id=request.GET["instance"]) if "instance" in request.GET else None

        form = cls(
            request.POST or None,
            instance=inst,
        )
        if "InfoPage" in dir(form):
            matchingObjs = [
                x
                for x in obj.objects.all()
                if x.InfoPage == form.InfoPage and x.Title == form.Title
            ]
        else:
            matchingObjs = ["this"]
        if form.is_valid() and len(matchingObjs) == 1:
            form.save()
        context["form"] = form

        response = (
            render(request, "media/form.html", context)
            if request.method == "GET"
            else redirect(request.META.get("HTTP_REFERER", "/media"))
        )
    return response


@login_required
def edit(request) -> HttpResponse:
    response: HttpResponse = redirect(request.META.get("HTTP_REFERER", "/media"))
    if contentObj := FindID(request.GET.get("id", -1)):
        cls = FormMatch(contentObj)

        form = cls(request.POST or None, instance=contentObj)
        if form.is_valid():
            form.save()
        context = {}
        context["form"] = form
        context["inst"] = contentObj
        context["colorMode"] = request.COOKIES.get("colorMode", "dark")
        contentObj.GetLogo("www." in contentObj.Logo or "://" in contentObj.Logo)

        response = (
            render(request, "media/editForm.html", context)
            if request.method == "GET"
            else redirect("/media")
        )
        if request.POST:
            SortTags(contentObj)
            if contentObj.Rating > 0:
                contentObj.Watched = True
            LOGGER.info("Edited %s", contentObj.Title)

    return response


@login_required
def SetBool(request) -> HttpResponse:
    response: HttpResponse = redirect(request.META.get("HTTP_REFERER", "/media"))
    if contentObj := FindID(request.GET.get("contentId", -1)):
        if request.POST.get("rating", None):
            contentObj.Rating = float(request.POST.get("rating", contentObj.Rating))
            contentObj.Genre_Tags = request.POST.get("Genre_Tags", contentObj.Genre_Tags)
            contentObj.Watched = True
            contentObj.save()
            response = redirect("/media")
        elif request.GET.get("field", None):
            field = request.GET.get("field")
            newValue = (
                request.GET.get("value", "False") == "True"
                if "value" in request.GET
                else not getattr(contentObj, field)
            )
            if field == "Watched":
                if newValue:
                    response = render(
                        request,
                        "media/rating.html",
                        {"obj": contentObj, "colorMode": request.COOKIES.get("colorMode", "dark")},
                    )
                else:
                    contentObj.Rating = 0
                    setattr(contentObj, field, newValue)
            else:
                setattr(contentObj, field, newValue)

            contentObj.save()

    return response


def index(request: HttpRequest, media="Movie") -> HttpResponse:
    if media[-1].lower() == "s":
        media = media[:-1]
    if media.lower() not in [x.__name__.lower() for x in MODEL_LIST]:
        return HttpResponseNotFound()

    _formType, objType = GetFormAndClass(media)

    if sortKey := request.GET.get("sort", None):
        if sortKey not in dir(objType.objects.first()) + DEFAULT_SORT_TERMS:
            redirectLink = f"/media/{media.lower()}s"
            for key, value in request.GET.items():
                if "?" not in redirectLink:
                    redirectLink += "?"
                if key != "sort":
                    redirectLink += f"{key}={value}&"
            return redirect(redirectLink)

    context = FilterMedia(request=request, objType=objType)
    context["colorMode"] = request.COOKIES.get("colorMode", "dark")
    pageSize: int = int(
        request.GET.get(
            "pageSize", 36 if "iPhone" not in request.headers.get("User-Agent", "") else 12
        )
    )

    pageNumber: int = int(request.GET.get("page", 1))
    context["page_obj"] = Paginator(context["obj_list"], pageSize).get_page(pageNumber)
    context["loggedIn"] = request.user.is_authenticated
    return render(
        request,
        "media/pagedView.html",
        context,
    )
