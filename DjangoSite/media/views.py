# pylint: disable=C0103
import logging

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render

from .modules.DB_Tools import CleanDupes
from .modules.ModelTools import DownloadImage, SortTags
from .modules.UpdateFromFolder import UpdateFromFolder
from .modules.Utils import (
    MODEL_LIST,
    DetermineForm,
    FindID,
    FormMatch,
    GetAllTags,
    GetContents,
    GetFormAndClass,
)
from .modules.WebTools import ScrapeWiki
from .utils import ExtractYearRange, FilterTags, FuzzStr, SearchFunction, SortFunction

# Create your views here.
LOGGER = logging.getLogger("Simple")


def viewMedia(request) -> HttpResponse:
    context = {"object": FindID(request.GET.get("id", -1))}
    context["colorMode"] = request.COOKIES.get("colorMode", "dark")

    return render(request, "media/mediaPage.html", context)


def fullView(request) -> HttpResponse:
    soloContent = request.GET.get("type", None)
    context = {
        "MediaTypes": (
            GetContents(request=request)
            if soloContent is None
            else GetContents(request=request)[soloContent]
        ),
        "Graphs": "noGraphs" in request.GET,
        "Tags": GetAllTags() if "genre" not in request.GET else {},
    }
    context["colorMode"] = request.COOKIES.get("colorMode", "dark")

    return render(request, "media/index.html", context)


@login_required
def update(request) -> HttpResponse:
    if "clean" not in request.GET:
        response = UpdateFromFolder(
            folder=r"W:/", useFile="useFile" in request.GET, save="save" in request.GET
        )
    else:
        _, model = GetFormAndClass(request.GET.get("type", "Movie"))
        response = CleanDupes(model=model)  # type:ignore
    return HttpResponse(content=response, content_type="text/plain")


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
                else:
                    LOGGER.error("Wiki load failed from %s", activeForm.data["InfoPage"])
            else:
                LOGGER.warning("Matching Object Found")
            returnRender = redirect("/media?sort=Date+Added")
    return returnRender


def poll(_request) -> HttpResponse:
    return redirect("https://www.youtube.com/watch?v=sVjk5nrb_lI")


@login_required
def backup(_request) -> HttpResponse:
    backupDict = {}
    for model in MODEL_LIST:
        # pylint: disable=E1101
        backupDict[model.__name__] = [x.JsonRepr for x in model.objects.all()]
    return JsonResponse(data=backupDict)


def stats(request) -> HttpResponse:
    context = {}
    for media in MODEL_LIST:
        context[media.__name__] = FilterMedia(request, media)["obj_list"]
    context["colorMode"] = request.COOKIES.get("colorMode", "dark")
    return render(request, "media/stats.html", context=context)


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

        contentObj.GetLogo(True)

        response = (
            render(request, "media/editForm.html", context)
            if request.method == "GET"
            else redirect("/media")
        )
        if request.POST:
            SortTags(contentObj)
            LOGGER.warning("Edited %s", contentObj.Title)

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
    return render(
        request,
        "media/pagedView.html",
        context,
    )


def FilterMedia(request, objType) -> dict:
    # pylint: disable=E1101

    sortKey: str = request.GET.get("sort", "Title")
    genre: str = request.GET.get("genre", "")
    exclude: str = request.GET.get("exclude", "")
    query: str = request.GET.get("query", "")
    reverseSort: bool = request.GET.get("reverse", "false") == "true"
    objList = list(objType.objects.all())
    yearRange, objList = ExtractYearRange(request, objList)

    if query:
        objList = [x for x in objList if SearchFunction(subStr=x, tagStr=query)]
        objList = sorted(objList, key=lambda x: FuzzStr(x, query))

    genre, objList = FilterTags(genre, objList, include=True)
    exclude, objList = FilterTags(exclude, objList, include=False)

    if sortKey in ["Rating", "Genre Tags", "Date Added"]:
        reverseSort = not reverseSort
        if sortKey == "Rating":
            objList = [x for x in objList if x.Rating > 0]

    objList = sorted(objList, key=lambda x: SortFunction(obj=x, key=sortKey), reverse=reverseSort)
    return {
        "type": request.GET.get("type", "Movie"),
        "sort": sortKey,
        "reverse": reverseSort,
        "obj_list": objList,
        "Tags": GetAllTags(objType=objType),
        "filters": {
            "include": genre,
            "exclude": exclude,
            "minYear": yearRange.start,
            "maxYear": yearRange.stop,
        },
    }
