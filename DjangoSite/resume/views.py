from django.conf import settings
from django.http import FileResponse, HttpResponse
from django.shortcuts import redirect, render

from .models import Education, Employment, Proficiency, SkillsAndTools

# Create your views here.


# def resume(request) -> HttpResponse:
# context: dict = {
#     "Education": sorted(
#         Education.objects.all(),
#         key=lambda x: x.End_Year if x.End_Year > 0 else 999999,
#         reverse=True,
#     ),
#     "Employment": sorted(
#         Employment.objects.all(),
#         key=lambda x: x.End_Year if x.End_Year > 0 else 999999,
#         reverse=True,
#     ),
#     "Tools": sorted(
#         SkillsAndTools.objects.all(),
#         key=lambda x: x.Name,
#         reverse=False,
#     ),
#     "ProfLevels": Proficiency,
# }
# return render(request, "resume/resume.html", context)
# return redirect(request, "/")


def pdf(_request) -> FileResponse:
    return FileResponse((settings.SYNC_PATH / "resume.pdf").open(mode="rb"))


def resume(_request) -> HttpResponse:
    return HttpResponse((settings.SYNC_PATH / "resume.html").open(mode="rb"))
