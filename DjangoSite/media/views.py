# pylint: disable=C0103
import logging
import time

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseNotFound, JsonResponse
from django.shortcuts import redirect, render

from .models import Movie, TVShow
from .modules.CheckDetails import (CheckMovies, CheckTV, CopyOverRenderQueue,
                                   HandleReRenderQueue)
from .modules.FileRip import RipWDrive
from .modules.ModelTools import DownloadImage, SortTags
from .modules.Utils import (MODEL_LIST, DetermineForm, FindID, FormMatch,
                            GetAllTags, GetContents, GetFormAndClass)
from .modules.WebTools import ScrapeWiki
from .utils import (ExtractYearRange, FilterTags, FuzzStr, SearchFunction,
                    SortFunction)

# Create your views here.
LOGGER = logging.getLogger("UserLogger")


def viewMedia(request) -> HttpResponse:
    context = {"object": FindID(request.GET.get("id", -1))}
    context["colorMode"] = request.COOKIES.get("colorMode", "dark")

    return render(request, "media/mediaPage.html", context)


def fullView(request) -> HttpResponse:
    soloContent = request.GET.get("type", None)
    masterTags = {}
    for i in MODEL_LIST:
        for _title, valDict in GetAllTags(i, request.user.is_authenticated).items():
            masterTags |= valDict

    context = {
        "MediaTypes": (
            GetContents(request=request)
            if soloContent is None
            else GetContents(request=request)[soloContent]
        ),
        "Graphs": "noGraphs" in request.GET,
        "Tags": masterTags if "genre" not in request.GET else {},
    }
    context["colorMode"] = request.COOKIES.get("colorMode", "dark")

    return render(request, "media/index.html", context)


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
                else:
                    LOGGER.error("Wiki load failed from %s", activeForm.data["InfoPage"])
            else:
                LOGGER.warning("Matching Object Found for %s, Not Added", activeForm.data["Title"])
            returnRender = redirect(
                f"/media?sort=Date+Added&type={request.GET.get('type', 'Movie')}"
            )
    return returnRender


def adjustTags(_request):
    adjustDict = {
        "Gangster": "Mafia",
    }
    # pylint: disable=E1101
    for m in Movie.objects.all():
        for tag, replacement in adjustDict.items():
            m.Genre_Tags = m.Genre_Tags.replace(tag, replacement)
        m.save()
    return redirect("/media")


def checkFiles(request) -> HttpResponse:
    if request.GET.get("renderList", "False") == "True":
        HandleReRenderQueue()
        return HttpResponse("Rendered to File")
    if request.GET.get("copyList", "False") == "True":
        CopyOverRenderQueue()
        return HttpResponse("Copied Render List")

    if request.GET.get("Scan", "True") == "True":
        RipWDrive(request.GET.get("type","Movie"), showProgress=request.GET.get("progress",False))

    match request.GET.get("type"):
        case "TVShow":
            unmatched, matched = CheckTV()
        case _others:
            unmatched, matched = CheckMovies()

    ids = [x["Match"]["ID"] for x in matched]
    # pylint: disable=E1101
    objList = Movie.objects.all() if request.GET.get("type") != "TVShow" else TVShow.objects.all()
    wronglyMarked = [
        x for x in objList if x.Downloaded and x.id not in ids  # type:ignore
    ]

    return render(
        request=request,
        template_name="media/checkFile.html",
        context={"matched": matched, "unmatched": unmatched, "wronglyMarked": wronglyMarked},
    )


@login_required
def backup(_request) -> HttpResponse:
    backupDict = {}
    for model in MODEL_LIST:
        # pylint: disable=E1101
        backupDict[model.__name__] = [x.JsonRepr for x in model.objects.all()]
    return JsonResponse(data=backupDict)


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
    response: HttpResponse = redirect(request.META.get("HTTP_REFERER", "/media"))
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
        context = {}
        context["form"] = form
        context["colorMode"] = request.COOKIES.get("colorMode", "dark")
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


def index(request) -> HttpResponse:
    _formType, objType = GetFormAndClass(request.GET.get("type", "Movie"))
    context = FilterMedia(request=request, objType=objType)
    context["colorMode"] = request.COOKIES.get("colorMode", "dark")
    pageSize: int = int(request.GET.get("pageSize", 36))
    pageNumber: int = int(request.GET.get("page", 1))
    paginator = Paginator(context["obj_list"], pageSize)
    context["page_obj"] = paginator.get_page(pageNumber)
    context["loggedIn"] = request.user.is_authenticated
    return render(
        request,
        "media/pagedView.html",
        context,
    )


def FilterMedia(request, objType) -> dict:
    # pylint: disable=E1101

    sortKey: str = request.GET.get("sort", "Title")
    reverseSort: bool = request.GET.get("reverse", "false") == "true"
    objList = list(objType.objects.all())
    yearRange, objList = ExtractYearRange(request, objList)

    genre, objList = FilterTags(
        request.GET.get("genre", ""),
        objList,
        include=True,
    )
    exclude, objList = FilterTags(
        request.GET.get("exclude", ""),
        objList,
        include=False,
    )

    if query := request.GET.get("query", None):
        objList = [x for x in objList if SearchFunction(subStr=x, tagStr=query)]
        objList = sorted(objList, key=lambda x: FuzzStr(x, query), reverse=True)
        sortKey = f"Search {query}"
    else:
        if sortKey in ["Rating", "Genre Tags", "Date Added"]:
            reverseSort = not reverseSort
            if sortKey == "Rating":
                objList = [x for x in objList if x.Rating > 0]
        objList = sorted(
            objList, key=lambda x: SortFunction(obj=x, key=sortKey), reverse=reverseSort
        )
    return {
        "type": request.GET.get("type", "Movie"),
        "sort": sortKey,
        "reverse": reverseSort,
        "obj_list": objList,
        "Tags": GetAllTags(objType=objType, loggedIn=request.user.is_authenticated),
        "filters": {
            "include": genre,
            "exclude": exclude,
            "minYear": yearRange.start,
            "maxYear": yearRange.stop,
        },
    }
