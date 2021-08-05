from django.shortcuts import render


def about_us(request):
    context = {"some_information": ["bla bla bla bla bla bla bla bla bla bla"]}
    return render(request, "about_us.html", context)


def contacts(request):
    context = {
        "some_information": ["tel. +2346345647", "Kyiv, Ukraine", "Lavrskya str."]
    }
    return render(request, "contacts.html", context)


def authors(request):
    context = {
        "some_information": ["Han Solo", "Homer J. Simpson", "Radjit Kutrapalli"]
    }
    return render(request, "authors.html", context)


def home(request):
    context = {"some_information": ["about-us", "contacts", "authors"]}
    return render(request, "home.html", context)
