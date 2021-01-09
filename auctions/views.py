from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms

from .models import User, Listing, Category


class CreateListing(forms.Form):
    title = forms.CharField(max_length=64, widget=forms.TextInput(attrs={
        "class": "form-control col-md-8 col-md-lg-8"
    }))
    description = forms.CharField(max_length=200, widget=forms.Textarea(attrs={
        "class": "form-control col-md-8 col-lg-8", "rows": 10
    }))
    image = forms.ImageField()
    category = forms.ModelChoiceField(queryset=Category.objects.all())
    starting_price = forms.IntegerField()


class Bid(forms.Form):
    bid_form = forms.IntegerField()


def index(request):
    if request.user.is_authenticated:
        listings = Listing.objects.all().filter(open_at=True)
    else:
        listings = Listing.objects.all().filter(open_at=True)
    return render(request, "auctions/index.html", {
        "listings": listings
    })


def bid(request, listing_id):
    error_clean_bid = False
    listing = Listing.objects.get(pk=listing_id)
    if request.method == "POST":
        form = Bid(request.POST)
        if form.is_valid():
            clean_bid = form.cleaned_data["bid_form"]
            price_from_database = listing.starting_price
            if clean_bid > price_from_database:
                listing.starting_price = clean_bid
                listing.save()
            else:
                error_clean_bid = True
    else:
        form = Bid()
    return render(request, "auctions/bid.html", {
        "listing": listing,
        "form": form,
        "error_clean_bid": error_clean_bid
    })


def create_listing(request):
    if request.method == "POST":
        form = CreateListing(request.POST, request.FILES)
        if form.is_valid():
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            category = form.cleaned_data["category"]
            image = form.cleaned_data["image"]
            final_price = form.cleaned_data["final_price"]
            starting_price = form.cleaned_data["starting_price"]
            p = Listing(title=title, description=description,
                        category_id=category, image=image, owner=request.user,
                        final_price=final_price, starting_price=starting_price)
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
