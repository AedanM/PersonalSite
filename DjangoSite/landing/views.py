from django.http import HttpResponse
from django.shortcuts import render


# Create your views here.
def index(request) -> HttpResponse:
    context: dict = {"colorMode": request.COOKIES.get("colorMode", "dark")}
    return render(request, "landing/index.html", context)


def iterLink(request):
    link = request.GET.get("link")
    start = int(request.GET.get("start", 0))
    end = int(request.GET.get("end", 10)) + 1
    linkList = [link.replace("{idx}", str(x)) for x in range(start, end)]
    context: dict = {"colorMode": request.COOKIES.get("colorMode", "dark"), "linkList": linkList}
    return render(request, "landing/iterLink.html", context)
