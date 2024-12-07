import logging

from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_protect

LOGGER = logging.getLogger("UserLogger")


@csrf_protect
def loginView(request):
    nextPage = request.GET.get("next", "/media")
    context: dict = {"colorMode": request.COOKIES.get("colorMode", "dark")}
    loggedIn = False
    if request.method == "POST":
        user = authenticate(
            request, username=request.POST["username"], password=request.POST["password"]
        )
        if user:
            login(request, user)
            LOGGER.info("%s Logged In", user.get_full_name())
            loggedIn = True

    if loggedIn or request.user.is_authenticated:
        return redirect(nextPage)
    LOGGER.error("USER NOT AUTH")
    return render(request, "accountPages/login.html", context=context)


@csrf_protect
def logoutView(request):
    logout(request=request)
    dst = request.GET.get("next", "/")
    return redirect(dst)
