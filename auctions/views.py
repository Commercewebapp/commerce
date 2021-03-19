from datetime import datetime, timezone, timedelta

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.db import IntegrityError
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from commerce.settings import LOGIN_URL

from .forms import CreateListing, BidForm, CommentForm
from .models import User, Listing, Category, Comment, Bid, Flag
from .spam_word import spam


class BidView(View):
    @method_decorator(login_required(login_url=LOGIN_URL))
    def get(self, request, **kwargs):
        """
        Load listing, check user is owner, check bidder and non-bidder on
        the listing and check if image two exist.

        Listing contain three images.
        Owner can't 'bid' and 'add watch list' on own listing.
        Image two exist is for rendering the images, if user added just one
        image then the html will not render the black border for the image.
        Names of bidder is for tracking who is bidder and non-bidder on the
        listing.
        """
        listing = get_object_or_404(Listing, pk=self.kwargs["listing_id"])
        bidder = listing.bids.all()
        matches_user = (listing.owner == request.user)
        image_two_exist = (listing.image_two != "image_two")
        names_of_bidder = [user_name.user.username for user_name in bidder]
        return render(request, "auctions/bid.html", {
            "listing": listing,
            "bid_form": BidForm(),
            "comment_form": CommentForm(),
            "matches_user": matches_user,
            "bid_count": bidder.count(),
            "names_of_bidder": names_of_bidder,
            "image_two_exist": image_two_exist
        })

    @method_decorator(login_required(login_url=LOGIN_URL))
    def post(self, request, **kwargs):
        """Request.method == 'POST'"""
        bid_form = BidForm(request.POST)
        listing = get_object_or_404(Listing, pk=self.kwargs["listing_id"])
        if bid_form.is_valid():
            bid_amount = bid_form.cleaned_data["bid"]
            return self.update_bid(request, bid_amount, listing, bid_form)
        return HttpResponseRedirect(reverse("bid", args=(listing.id,)))

    def place_bid(self, request, bid_amount, listing, current_time):
        if bid_amount - listing.current_price() >= 1:
            listing.bids.update(date=current_time)
            recent_bid = Bid.objects.create(date=current_time, listing=listing,
                                            bid=bid_amount, user=request.user)
            Listing.objects.filter(pk=self.kwargs["listing_id"]).update(
                winning_bid=recent_bid.id)
            error_clean_bid = False
        else:
            error_clean_bid = True
        return error_clean_bid

    def update_bid(self, request, bid_amount, listing, bid_form):
        """When user click bid"""
        bid_count = listing.bids.all().count()
        user_bid = listing.bids.filter(user=request.user).first()
        current_time = datetime.now(timezone.utc)
        error_clean_bid = False
        wait_for_three_min = False
        if user_bid is None:
            error_clean_bid = self.place_bid(request, bid_amount, listing,
                                             current_time)
        else:
            delta = current_time - user_bid.date
            can_place_bid = delta > timedelta(minutes=1)
            if can_place_bid:
                error_clean_bid = self.place_bid(request, bid_amount, listing,
                                                 current_time)
            else:
                wait_for_three_min = True
        return render(request, "auctions/bid.html", {
            "listing": listing,
            "bid_form": bid_form,
            "wait_for_three_min": wait_for_three_min,
            "error_clean_bid": error_clean_bid,
            "comment_form": CommentForm(),
            "bid_count": bid_count
        })


def index(request):
    """Active listing tab"""
    listings = Listing.objects.filter(open_at=True)
    get_client_ip(request)
    return render(request, "auctions/index.html", {"listings": listings})


@login_required(login_url=LOGIN_URL)
def get_client_ip(request):
    """Get IP"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    User.objects.filter(pk=request.user.id).update(ip=ip)
    # Block IP address
    blocked_ip = ['']
    for i in range(len(blocked_ip)):
        if ip == blocked_ip[i]:
            logout(request)
            return HttpResponse("You're not allow on the site")
    return HttpResponseRedirect(reverse("index"))


def hot_listing_view(request):
    """Checking for HOT listing"""
    listings = Listing.objects.all()
    allow_hot_listing = 5
    for listing in listings:
        bid_count = listing.bids.all().count()
        if bid_count > allow_hot_listing:
            Listing.objects.filter(pk=listing.id).update(hot=True)
    # HOT listing tab
    listings = Listing.objects.filter(hot=True, open_at=True)
    return render(request, "auctions/hot_listing.html", {"listings": listings})


def auto_close_listing() -> None:
    """Automatic closing system for listing"""
    listings = Listing.objects.all()
    current_date = datetime.now(timezone.utc).date()
    for listing in listings:
        listing_ended = listing.end_date == current_date
        if listing_ended:
            Listing.objects.filter(pk=listing.id).update(open_at=False)


def search(request):
    """Search bar on index.html(Active Listing)"""
    listings = Listing.objects.all()
    value = request.GET.get('q', '')
    if Listing.objects.filter(title=str(value)).first() is not None:
        return HttpResponseRedirect(reverse("index"))
    sub_string_listings = []
    for listing in listings:
        if value.upper() in listing.title.upper():
            sub_string_listings.append(listing)
    return render(request, "auctions/index.html", {
        "search_listings": sub_string_listings,
        "search": True,
        "value": value
    })


def category_view(request):
    """Category tab"""
    categories = Category.objects.all()
    return render(request, "auctions/category.html", {"categories": categories})


def each_category_listing(request, category_id):
    """Render category list, Category tab"""
    listings = Listing.objects.filter(category=category_id, open_at=True)
    return render(request, "auctions/each_category.html",
                  {"listings": listings})


@login_required(login_url=LOGIN_URL)
def own_listing(request):
    """The listing that user post, Own Listing tab"""
    listings = Listing.objects.filter(owner=request.user)
    return render(request, "auctions/own_listing.html", {"listings": listings})


@login_required(login_url=LOGIN_URL)
def flag_listing(request, listing_id):
    """Report button on listing"""
    listing = Listing.objects.get(pk=listing_id)
    listing_flagged = listing.flags.filter().first()
    matches_user = listing.owner == request.user
    if matches_user:
        return HttpResponseRedirect(reverse("bid", args=(listing.id,)))
    if listing_flagged is None:
        Flag.objects.create(flag_count=1, listing=listing,
                            user=request.user)
    user_flagged = Flag.objects.filter(user=request.user,
                                       listing=listing_id).first()
    flag_amount = listing.flags.get().flag_count
    settings.max_flag = 3
    if flag_amount <= settings.max_flag and user_flagged is None:
        flag_amount += 1
        listing.flags.update(flag_count=flag_amount, user=request.user)
    else:
        cannot_flag = True
        bid_form = BidForm()
        return render(request, "auctions/bid.html", {
            "cannot_flag": cannot_flag,
            "listing": listing,
            "bid_form": bid_form
        })
    if flag_amount >= settings.max_flag:
        Listing.objects.filter(pk=listing_id).update(open_at=False)
    return HttpResponseRedirect(reverse("bid", args=(listing.id,)))


@login_required(login_url=LOGIN_URL)
def comment(request, listing_id):
    """Save comment is database, when comment button is click"""
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            clean_comment = form.cleaned_data["comment"]
            listing = Listing.objects.get(pk=listing_id)
            Comment.objects.create(user=request.user, comment=clean_comment,
                                   listing=listing)
    return HttpResponseRedirect(reverse("bid", args=(listing.id,)))


@login_required(login_url=LOGIN_URL)
def watchlist(request, listing_id):
    """Add on watchlist, when watch list button is click"""
    if request.method == "POST":
        listing = Listing.objects.get(pk=listing_id)
        request.user.watch_listing.add(listing)
        return HttpResponseRedirect(reverse("watchlist_view"))
    return render(request, "auctions/watchlist.html")


@login_required(login_url=LOGIN_URL)
def remove_watchlist(request, listing_id):
    """Remove on watchlist, when remove watch list button is click"""
    if request.method == "POST":
        listing = Listing.objects.get(pk=listing_id)
        request.user.watch_listing.remove(listing)
        return HttpResponseRedirect(reverse("watchlist_view"))
    return render(request, "auctions/watchlist.html")


@login_required(login_url=LOGIN_URL)
def watchlist_view(request):
    """Render watch listing for user, Watch List tab"""
    user_watch_listing = request.user.watch_listing.all().filter(open_at=True)
    return render(request, "auctions/watchlist.html",
                  {"user_watch_listing": user_watch_listing})


@login_required(login_url=LOGIN_URL)
def close_bid(request, listing_id):
    """Close the listing, when close bid button is click"""
    if request.method == "POST":
        Listing.objects.filter(pk=listing_id, owner=request.user).update(
            open_at=False)
        return HttpResponseRedirect(reverse("close_bid_view"))
    return render(request, "auctions/close_bid.html")


@login_required(login_url=LOGIN_URL)
def close_bid_view(request):
    """Render listing that have been close, Close Bid tab"""
    listings = request.user.listing_set.all().filter(open_at=False)
    return render(request, "auctions/close_bid.html", {"listings": listings})


@login_required(login_url=LOGIN_URL)
def create_listing(request):
    """When user create listing"""
    # First time when user visit the page
    if Category.objects.exists() is False:
        default_category = ["Programming", "Fashion", "Christmas",
                            "Electronics", "Property", "Sport"]
        for category in default_category:
            Category.objects.create(name=category)
    spam_word_error = False
    # Creating listing
    if request.method == "POST":
        form = CreateListing(request.POST, request.FILES)
        if form.is_valid():
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            category = form.cleaned_data["category"]
            image = form.cleaned_data["image"]
            starting_price = form.cleaned_data["starting_price"]
            if str(title.lower()) in spam or str(description.lower()) in spam:
                spam_word_error = True
            else:
                Listing.objects.create(title=title, description=description,
                                       category=category, image=image,
                                       owner=request.user,
                                       starting_price=starting_price)
                return HttpResponseRedirect(reverse("index"))
    else:
        form = CreateListing()
    return render(request, "auctions/create_listing.html", {
        "form": form,
        "spam_word_error": spam_word_error
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
            return get_client_ip(request)
        return render(request, "auctions/login.html", {
            "message": "Invalid username and/or password."
        })
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
    return render(request, "auctions/register.html")
