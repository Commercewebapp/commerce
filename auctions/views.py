from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from datetime import datetime, timezone, timedelta
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import User, Listing, Category, Comment, Bid
from .form import CreateListing, BidForm, CommentForm


def index(request):
    listings = Listing.objects.filter(open_at=True)
    return render(request, "auctions/index.html", {
        "listings": listings
    })


def category_view(request):
    categories = Category.objects.all()
    return render(request, "auctions/category.html", {
        "categories": categories
    })


def each_category_listing(request, category_id):
    listings = Listing.objects.filter(category_id=category_id)
    return render(request, "auctions/each_category.html", {
        "listings": listings
    })


@login_required(login_url='/login')
def comment(request, listing_id):
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            clean_comment = form.cleaned_data["comment_box"]
            listing = Listing.objects.get(pk=listing_id)
            p = Comment(user=request.user, comment=clean_comment,
                        listing=listing)
            p.save()
            return HttpResponseRedirect(reverse("bid", args=(listing.id,)))
    else:
        CommentForm()


@login_required(login_url='/login')
def bid(request, listing_id):
    error_clean_bid = False
    wait_for_three_min = False
    owner_cant_bid = False
    listing = get_object_or_404(Listing, pk=listing_id)
    matches_user = listing.owner == request.user
    if request.method == "POST":
        comment_form = CommentForm()
        bid_form = BidForm(request.POST)
        if bid_form.is_valid():
            clean_bid = bid_form.cleaned_data["bid_form"]
            bid_from_user = listing.bids.filter(user=request.user).first()
            if bid_from_user is None:
                can_place_bid = True
            else:
                current_time = datetime.now(timezone.utc)
                record_date = listing.bids.filter(user=request.user).first().date
                delta = current_time - record_date
                can_place_bid = delta > timedelta(minutes=3)
            if can_place_bid:
                if clean_bid - listing.current_price() >= 2:
                    listing.bids.filter().update(date=current_time)
                    listing.save()
                    Bid.objects.create(date=current_time, listing=listing,
                                       bid=clean_bid, user=request.user)
                    Listing.objects.filter(pk=listing_id).update(winning_bid=listing.bids.order_by("-bid").first().id)
                else:
                    error_clean_bid = True
            else:
                wait_for_three_min = True
    else:
        if matches_user:
            owner_cant_bid = True
            bid_form = BidForm()
            comment_form = CommentForm()
        else:
            bid_form = BidForm()
            comment_form = CommentForm()
    return render(request, "auctions/bid.html", {
        "matches_user": matches_user,
        "listing": listing,
        "wait_for_three_min": wait_for_three_min,
        "bid_form": bid_form,
        "error_clean_bid": error_clean_bid,
        "comment_form": comment_form,
        "owner_cant_bid": owner_cant_bid,
    })


@login_required(login_url='/login')
def watchlist(request, listing_id):
    if request.method == "POST":
        listing = Listing.objects.get(pk=listing_id)
        request.user.watch_listing.add(listing)
        return HttpResponseRedirect(reverse("watchlist_view"))
    else:
        return render(request, "auctions/watchlist.html")


@login_required(login_url='/login')
def remove_watchlist(request, listing_id):
    if request.method == "POST":
        listing = Listing.objects.get(pk=listing_id)
        request.user.watch_listing.remove(listing)
        return HttpResponseRedirect(reverse("watchlist_view"))
    else:
        return render(request, "auctions/watchlist.html")


@login_required(login_url='/login')
def watchlist_view(request):
    return render(request, "auctions/watchlist.html", {
        "user_watch_listing": request.user.watch_listing.all().filter(open_at=True)
    })


@login_required(login_url='/login')
def close_bid(request, listing_id):
    if request.method == "POST":
        Listing.objects.filter(pk=listing_id, owner=request.user).update(open_at=False)
        return HttpResponseRedirect(reverse("close_bid_view"))
    else:
        return render(request, "auctions/close_bid.html")


@login_required(login_url='/login')
def close_bid_view(request):
    return render(request, "auctions/close_bid.html", {
        "listings": request.user.listing_set.all().filter(open_at=False),
    })


@login_required(login_url='/login')
def create_listing(request):
    if Category.objects.exists() is False:
        default_category = ["Programming", "Fashion", "Christmas",
                            "Electronics", "Property", "Sport"]
        for category in default_category:
            p = Category(name=category)
            p.save()
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
