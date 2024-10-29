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


# # Create your views here.
# def Login(request) -> HttpResponse:
#     if request.method == "POST":

#         # AuthenticationForm_can_also_be_used__

#         username = request.POST["username"]
#         password = request.POST["password"]
#         user = authenticate(request, username=username, password=password)
#         if user is not None:
#             form = login(request, user)
#             messages.success(request, f" welcome {username} !!")
#             return redirect("index")
#         else:
#             messages.info(request, f"account done not exit plz sign in")

#     form = AuthenticationForm()
#     context: dict = {
#         "colorMode": request.COOKIES.get("colorMode", "dark"),
#         "form": form,
#         "title": "log in",
#     }
#     return render(request, "accounts/login.html", context)
