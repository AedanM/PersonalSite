from django.http import HttpResponse
from django.shortcuts import render

from .models import Education, Employment, Proficiency, SkillsAndTools

# Create your views here.


def resume(request) -> HttpResponse:
    context: dict = {
        "Education": sorted(
            Education.objects.all(),
            key=lambda x: x.End_Year if x.End_Year > 0 else 999999,
            reverse=True,
        ),
        "Employment": sorted(
            Employment.objects.all(),
            key=lambda x: x.End_Year if x.End_Year > 0 else 999999,
            reverse=True,
        ),
        "Tools": sorted(
            SkillsAndTools.objects.all(),
        ),
        "ProfLevels": Proficiency,
    }
    print(context["Tools"])
    return render(request, "resume/resume.html", context)
