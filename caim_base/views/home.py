from django.shortcuts import render


def index(request):
    # return redirect('https://caim.org/')
    return render(
        request,
        "home.html",
        {
            "pageTitle": "Home",
            "navbarDark": True,
            "bodyClasses": "page-narrow",
            "disableFooter": True,
        },
    )
