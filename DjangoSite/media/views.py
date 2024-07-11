# pylint: disable=C0103

from django.http import HttpResponse
from django.shortcuts import redirect, render

from .modules.DB_Tools import CleanDupes
from .modules.UpdateFromFolder import UpdateFromFolder
from .modules.Utils import FindID, FormMatch, GetContents, GetFormAndClass
from .modules.WebTools import GetShowInfo

# Create your views here.


def viewMedia(request) -> HttpResponse:
    context = {"object": FindID(request.GET["id"])}
    return render(request, "media/mediaPage.html", context)


def index(request) -> HttpResponse:
    soloContent = request.GET["type"] if "type" in request.GET else None
    context = {
        "MediaTypes": (
            GetContents(request=request)
            if soloContent is None
            else GetContents(request=request)[soloContent]
        ),
        "Graphs": "noGraphs" in request.GET,
    }
    return render(request, "media/index.html", context)


def update(request) -> HttpResponse:
    if "clean" not in request.GET:
        response = UpdateFromFolder(
            folder=r"W:/", useFile="useFile" in request.GET, save="save" in request.GET
        )
    else:
        _, model = GetFormAndClass(request=request)
        response = CleanDupes(model=model)  # type:ignore
    return HttpResponse(content=response, content_type="text/plain")


def wikiScrape(request) -> HttpResponse:
    _, cls = GetFormAndClass(request=request)
    response = GetShowInfo(
        wikiLink=request.GET["show"] if "show" in request.GET else False, mediaType=cls
    )
    return HttpResponse(content=response, content_type="text/json")


def new(request) -> HttpResponse:
    response: HttpResponse = redirect("/media")
    if "type" in request.GET:
        cls, obj = GetFormAndClass(request)

        # pylint: disable=E1101
        inst = obj.objects.get(id=request.GET["instance"]) if "instance" in request.GET else None

        form = cls(request.POST or None, instance=inst)
        if form.is_valid():
            form.save()
        context = {}
        context["form"] = form
        response = (
            render(request, "media/form.html", context)
            if request.method == "GET"
            else redirect("/media")
        )

    return response


def edit(request) -> HttpResponse:
    response: HttpResponse = redirect("/media")
    if contentObj := FindID(request.GET["id"]):
        cls = FormMatch(contentObj)

        form = cls(request.POST or None, instance=contentObj)
        if form.is_valid():
            form.save()
        context = {}
        context["form"] = form
        context["inst"] = contentObj
        response = (
            render(request, "media/editForm.html", context)
            if request.method == "GET"
            else redirect("/media")
        )

    return response


def SetBool(request) -> HttpResponse:
    response: HttpResponse = redirect("/media")
    if "contentId" in request.GET and "field" in request.GET:
        if contentObj := FindID(request.GET["contentId"]):
            field = request.GET["field"]
            newValue = (
                request.GET["value"] == "True"
                if "value" in request.GET
                else not getattr(contentObj, field)
            )
            setattr(contentObj, field, newValue)
            contentObj.save()
    return response
