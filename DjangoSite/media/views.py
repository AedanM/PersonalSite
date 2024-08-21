# pylint: disable=C0103

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import redirect, render
from thefuzz import fuzz

from .forms import MovieForm
from .modules.DB_Tools import CleanDupes
from .modules.UpdateFromFolder import UpdateFromFolder
from .modules.Utils import (FindID, FormMatch, GetAllTags, GetContents,
                            GetFormAndClass)
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
        _, model = GetFormAndClass(request=request)
        response = CleanDupes(model=model)  # type:ignore
    return HttpResponse(content=response, content_type="text/plain")


@login_required
def wikiLoad(request) -> HttpResponse:
    context = {}
    returnRender = render(request, "media/wikiLoad.html")
    form, model = GetFormAndClass(request)
    if request.method == "POST":
        input_value = request.POST.get("Wiki Link", None)
        if input_value:
            contentDetails = ScrapeWiki(wikiLink=input_value)
            context["form"] = MovieForm(initial=contentDetails)
            context["colorMode"] = request.COOKIES.get("colorMode", "dark")

            returnRender = render(request, "media/form.html", context=context)
        else:
            activeForm = form(request.POST)
            if activeForm.is_valid():
                activeForm.save()
            # pylint: disable=E1101
            obj = [x for x in model.objects.all() if x.Title == request.POST.get("Title")]
            if obj:
                obj[0].GetLogo(True)
            returnRender = redirect("/media")
    return returnRender


@login_required
def new(request) -> HttpResponse:
    response: HttpResponse = redirect(request.META.get("HTTP_REFERER", "/media"))
    if request.GET.get("type", None):
        cls, obj = GetFormAndClass(request)

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
    if request.GET.get("contentId", None) and request.GET.get("field", None):
        if contentObj := FindID(request.GET.get("contentId", -1)):
            field = request.GET.get("field")
            newValue = (
                request.GET.get("value", "False") == "True"
                if "value" in request.GET
                else not getattr(contentObj, field)
            )
            setattr(contentObj, field, newValue)
            contentObj.save()
    return response


def SortFunction(obj, key: str):
    outObj = None
    match (key):
        case "Title":
            outObj = obj.SortTitle
        case "None":
            outObj = obj
        case "TagLen":
            outObj = len(obj.GenreTagList)
        case _others:
            outObj = getattr(obj, key)

    return outObj


def index(request) -> HttpResponse:
    colorMode = request.COOKIES.get("colorMode", "dark")
    pageSize: int = int(request.GET.get("pageSize", 36))
    pageNumber: int = int(request.GET.get("page", 1))
    sortKey: str = request.GET.get("sort", "Title")
    genre: str = request.GET.get("genre", "")
    exclude: str = request.GET.get("exclude", "")
    query: str = request.GET.get("query", "")
    reverseSort: bool = request.GET.get("reverse", "False") == "True"
    _formType, objType = GetFormAndClass(request)

    # pylint: disable=E1101
    objList = objType.objects.all()
    if query:
        objList = [x for x in objList if SearchFunction(subStr=x, tagStr=query)]
        objList = sorted(objList, key=lambda x: FuzzStr(x, query))
    if genre:
        objList = [x for x in objList if all(tag in str(x.Genre_Tags) for tag in genre.split(","))]
    if exclude:
        objList = [
            x for x in objList if not any(tag in str(x.Genre_Tags) for tag in exclude.split(","))
        ]

    if sortKey == "Rating":
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
            "filters" : {
                "include":genre,
                "exclude":exclude,
            }
        },
    )


def SearchFunction(subStr, tagStr):
    return all(FuzzStr(subStr, tag) > 75 for tag in tagStr.split(","))


def FuzzStr(obj, query):
    return fuzz.partial_ratio(query.lower(), f"{obj.Genre_Tags} {obj.Title}".lower())
