# pylint: disable=C0103


import datetime

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from thefuzz import fuzz

from .modules.DB_Tools import CleanDupes
from .modules.ModelTools import DownloadImage
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

# Create your views here.


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
    returnRender = render(request, "media/wikiLoad.html")
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
            if activeForm.is_valid():
                activeForm.save()
                # pylint: disable=E1101
                obj = model.objects.filter(Title=request.POST.get("Title")).first()
                if obj:
                    obj.Genre_Tags = ", ".join(sorted(obj.GenreTagList))
                    DownloadImage(obj)
                    obj.GetLogo(True)
            else:
                print(f"Invalid Form {activeForm.errors}")

            returnRender = redirect("/media")
    return returnRender


@login_required
def backup(_request) -> HttpResponse:
    backupDict = {}
    for model in MODEL_LIST:
        # pylint: disable=E1101
        backupDict[model.__name__] = [x.JsonRepr for x in model.objects.all()]
    return JsonResponse(data=backupDict)


def stats(request):
    context = {}
    for media in MODEL_LIST:
        # pylint: disable=E1101
        context[media.__name__] = media.objects.all()
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
        if form.is_valid():
            form.save()
        context = {}
        context["form"] = form
        context["colorMode"] = request.COOKIES.get("colorMode", "dark")
        response = (
            render(request, "media/form.html", context)
            if request.method == "GET"
            else redirect("/media")
        )
    else:
        print(request.POST.get("Title"))
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

    return response


@login_required
def SetBool(request) -> HttpResponse:
    response: HttpResponse = redirect(request.META.get("HTTP_REFERER", "/media"))
    if contentObj := FindID(request.GET.get("contentId", -1)):
        print(request.POST)

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


def SortFunction(obj, key: str):
    outObj = None
    key = key.replace(" ", "_")
    match (key):
        case "Title":
            outObj = obj.SortTitle
        case "None":
            outObj = obj
        case "Genre_Tags":
            outObj = len(obj.GenreTagList)
        case _others:
            outObj = getattr(obj, key)

    return outObj


def index(request) -> HttpResponse:
    # pylint: disable=E1101

    colorMode = request.COOKIES.get("colorMode", "dark")
    pageSize: int = int(request.GET.get("pageSize", 36))
    pageNumber: int = int(request.GET.get("page", 1))
    sortKey: str = request.GET.get("sort", "Title")
    genre: str = request.GET.get("genre", "")
    exclude: str = request.GET.get("exclude", "")
    query: str = request.GET.get("query", "")
    reverseSort: bool = request.GET.get("reverse", "False") == "True"
    _formType, objType = GetFormAndClass(request.GET.get("type", "Movie"))
    yearRange = range(
        int(request.GET.get("minYear", min(x.Year for x in objType.objects.all()))),
        int(request.GET.get("maxYear", datetime.datetime.now().year)) + 1,
    )
    objList = [x for x in objType.objects.all() if x.Year in yearRange]

    if query:
        objList = [x for x in objList if SearchFunction(subStr=x, tagStr=query)]
        objList = sorted(objList, key=lambda x: FuzzStr(x, query))

    genre, objList = FilterTags(genre, objList, include=True)
    exclude, objList = FilterTags(exclude, objList, include=False)

    if sortKey in ["Rating", "Genre Tags"]:
        reverseSort = not reverseSort
        objList = [x for x in objList if x.Rating > 0]
    objList = sorted(objList, key=lambda x: SortFunction(obj=x, key=sortKey), reverse=reverseSort)
    paginator = Paginator(objList, pageSize)
    page_obj = paginator.get_page(pageNumber)
    return render(
        request,
        "media/pagedView.html",
        {
            "page_obj": page_obj,
            "type": request.GET.get("type", "Movie"),
            "sort": sortKey,
            "reverse": reverseSort,
            "Tags": GetAllTags(),
            "colorMode": colorMode,
            "filters": {
                "include": genre,
                "exclude": exclude,
                "minYear": yearRange.start,
                "maxYear": yearRange.stop,
            },
        },
    )


def FilterTags(tagList, objList, include):
    if tagList:
        if "watched" in tagList:
            objList = [
                x for x in objList if (include and x.Watched) or (not include and not x.Watched)
            ]
            tagList = tagList.replace("watched", "").strip()

        if "downloaded" in tagList:
            objList = [
                x
                for x in objList
                if (include and x.Downloaded) or (not include and not x.Downloaded)
            ]
            tagList = tagList.replace("downloaded,", "").strip()
            tagList = tagList.replace("downloaded", "").strip()
        if tagList:
            objList = [
                x
                for x in objList
                if (include and CheckTags(x, tagList))
                or (not include and not ExcludeTags(x, tagList))
            ]

    return tagList, objList


def CheckTags(x, tagList):
    return all(tag in " ".join(x.GenreTagList) for tag in tagList.split(",") if tag)


def ExcludeTags(x, tagList):
    return any(tag in " ".join(x.GenreTagList) for tag in tagList.split(",") if tag)


def SearchFunction(subStr, tagStr):
    return all(FuzzStr(subStr, tag) > 75 for tag in tagStr.split(","))


def FuzzStr(obj, query):
    return fuzz.partial_ratio(query.lower(), f"{obj.Genre_Tags} {obj.Title}".lower())
