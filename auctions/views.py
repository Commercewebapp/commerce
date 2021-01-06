from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms

from .models import User, Listing


class CreateListing(forms.Form):
    title = forms.CharField(label="Title", max_length=100,
                            widget=forms.TextInput(attrs={
                                "class": "form-control col-md-8 col-md-lg-8"
                            }))
    description = forms.CharField(label="Description", max_length=200,
                                  widget=forms.Textarea(attrs={
                                      "class": "form-control col-md-8 col-lg-8",
                                      "rows": 10
                                  }))
    category = forms.ChoiceField(label="Category")


def index(request):
    if request.user.is_authenticated:
        listings = Listing.objects.all().filter(open_at=True)
    else:
        listings = Listing.objects.all().filter(open_at=True)
    return render(request, "auctions/index.html", {
        "listings": listings
    })


def create_listing(request):
    if request.method == "POST":
        form = CreateListing(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            p = Listing(title=title, description=description)
            p.save()
            return HttpResponseRedirect(reverse("index"))
    else:
        form = CreateListing()
    return render(request, "auctions/create_listing.html", {
        "form": form
    })


def login_view(request):
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })
        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
