from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render


def loginView(request):
    nextPage = request.GET.get("next", "/media")
    context: dict = {"colorMode": request.COOKIES.get("colorMode", "dark")}
    if request.method == "POST":
        user = authenticate(
            request, username=request.POST["username"], password=request.POST["password"]
        )
        if user:
            login(request, user)
            # messages.success(request, "Logged in successfully")
            return redirect(nextPage)
        else:
            ...
            # messages.error(request, "Logged in Fail")
    return render(request, "accountPages/login.html", context=context)
