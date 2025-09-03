from django.conf import settings
from django.http import FileResponse, HttpRequest, HttpResponse


def pdf(_request: HttpRequest) -> FileResponse:
    return FileResponse((settings.SYNC_PATH / "resume" / "resume.pdf").open(mode="rb"))


def resume(_request: HttpRequest) -> HttpResponse:
    return HttpResponse((settings.SYNC_PATH / "resume" / "resume.html").open(mode="rb"))
