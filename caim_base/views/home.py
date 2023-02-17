from django.shortcuts import redirect


def index(request):
    return redirect('https://caim.org/')
    # return render(
    #     request,
    #     "home.html",
    #     {
    #         "pageTitle": "Home",
    #         "navbarDark": True,
    #         "bodyClasses": "page-narrow",
    #     },
    # )
