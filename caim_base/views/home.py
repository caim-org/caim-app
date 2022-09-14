from django.shortcuts import render


def index(request):
    return render(
        request,
        "home.html",
        {
            "pageTitle": "Home",
            "navbarDark": True,
            "bodyClasses": "page-narrow",
        },
    )
