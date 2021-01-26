from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from datetime import datetime, timezone, timedelta

from .models import User, Listing, Category, Comment, Bid
from .form import CreateListing, BidForm, CommentForm


def index(request):
    listings = Listing.objects.all().filter(open_at=True)
    return render(request, "auctions/index.html", {
        "listings": listings
    })


def category_view(request):
    show_category = Category.objects.all()
    return render(request, "auctions/category.html", {
        "show_category": show_category
    })


def category_add(request, cate_id):
    listings = Listing.objects.filter(category_id=cate_id)
    return render(request, "auctions/each_category.html", {
        "listings": listings
    })


def comment(request, listing_id):
    if request.user.is_authenticated:
        listing = Listing.objects.get(pk=listing_id)
        if request.method == "POST":
            form = CommentForm(request.POST)
            if form.is_valid():
                clean_comment = form.cleaned_data["comment_box"]
                p = Comment(user=request.user, comment=clean_comment,
                            listing_title=listing)
                p.save()
                return HttpResponseRedirect(reverse("bid", args=(listing.id,)))
        else:
            CommentForm()
    else:
        return render(request, "auctions/bid.html")


def bid(request, listing_id):
    if request.user.is_authenticated:
        listing = Listing.objects.get(pk=listing_id)
        bid = listing.listing_bid.filter(track_user=request.user).first()
        current_time = datetime.now(timezone.utc)
        username = request.user.username
        matches_user = Listing.objects.filter(pk=listing_id,
                                              owner__username=username).exists()
        comment_message = listing.listing_com.all()
        error_clean_bid = False
        cant_bid = False
        wait_for_three_min = False
        if bid is None:
            p = Bid(date=current_time, listing=listing,
                    track_user=request.user)
            p.save()
        record_date = listing.listing_bid.filter(track_user=request.user).first().date
        if request.method == "POST":
            comment_form = CommentForm()
            form = BidForm(request.POST)
            if form.is_valid():
                clean_bid = form.cleaned_data["bid_form"]
                delta = current_time - record_date
                if delta > timedelta(minutes=3):
                    if clean_bid - listing.starting_price >= 2:
                        listing.listing_bid.filter().update(date=current_time)
                        listing.starting_price = clean_bid
                        listing.save()
                        Bid.objects.filter(pk=listing_id).update(track_user=request.user)
                    else:
                        error_clean_bid = True
                else:
                    wait_for_three_min = True
        else:
            if matches_user:
                cant_bid = True
                form = BidForm()
                comment_form = CommentForm()
            else:
                form = BidForm()
                comment_form = CommentForm()
        return render(request, "auctions/bid.html", {
            "matches_user": matches_user,
            "listing": listing,
            "wait_for_three_min": wait_for_three_min,
            "form": form,
            "error_clean_bid": error_clean_bid,
            "comment_form": comment_form,
            "cant_bid": cant_bid,
            "comment_message": comment_message
        })
    else:
        return render(request, "auctions/bid.html")


def watchlist(request, listing_id):
    if request.method == "POST":
        listing = Listing.objects.get(pk=listing_id)
        request.user.watch_listing.add(listing)
        return HttpResponseRedirect(reverse("watchlistview"))
    else:
        return render(request, "auctions/watchlist.html")


def removewatchlist(request, listing_id):
    if request.method == "POST":
        listing = Listing.objects.get(pk=listing_id)
        request.user.watch_listing.remove(listing)
        return HttpResponseRedirect(reverse("watchlistview"))
    else:
        return render(request, "auctions/watchlist.html")


def watchlistview(request):
    if request.user.is_authenticated:
        return render(request, "auctions/watchlist.html", {
            "user_watchlisting": request.user.watch_listing.all().filter(open_at=True)
        })
    else:
        return render(request, "auctions/watchlist.html")


def closebid(request, listing_id):
    if request.user.is_authenticated and request.method == "POST":
        Listing.objects.filter(pk=listing_id, owner=request.user).update(open_at=False)
        return HttpResponseRedirect(reverse("closebidview"))
    else:
        return render(request, "auctions/closebid.html")


def closebidview(request):
    if request.user.is_authenticated:
        listings = request.user.listing_set.all().filter(open_at=False)
        return render(request, "auctions/closebid.html", {
            "listings": listings
        })
    else:
        return render(request, "auctions/closebid.html")


def create_listing(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            form = CreateListing(request.POST, request.FILES)
            if form.is_valid():
                title = form.cleaned_data["title"]
                description = form.cleaned_data["description"]
                category = form.cleaned_data["category"]
                image = form.cleaned_data["image"]
                starting_price = form.cleaned_data["starting_price"]
                p = Listing(title=title, description=description,
                            category_id=category, image=image, owner=request.user,
                            starting_price=starting_price)
                p.save()
                return HttpResponseRedirect(reverse("index"))
        else:
            form = CreateListing()
        return render(request, "auctions/create_listing.html", {
            "form": form
        })
    else:
        return render(request, "auctions/create_listing.html")


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
        except ValueError:
            return render(request, "auctions/register.html", {
                "message": "Fill up the form."
            })
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
