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
        To use get(), you need 'listing_id' for getting individual listing
        """
        listing = get_object_or_404(Listing, pk=self.kwargs["listing_id"])
        bids = listing.bids.all()
        matches_user = (listing.owner == request.user)
        image_two_exist = (listing.image_two != "image_two")
        image_three_exist = (listing.image_three != "image_three")
        names_of_bidder = [user_name.user.username for user_name in bids]
        return render(request, "auctions/bid.html", {
            "listing": listing,
            "bid_form": BidForm(),
            "comment_form": CommentForm(),
            "matches_user": matches_user,
            "bid_count": bids.count(),
            "names_of_bidder": names_of_bidder,
            "image_two_exist": image_two_exist,
            "image_three_exist": image_three_exist
        })

    @method_decorator(login_required(login_url=LOGIN_URL))
    def post(self, request, **kwargs):
        """
        post() runs only when user submit the data to the site on bid.html
        """
        bid_form = BidForm(request.POST)
        listing = get_object_or_404(Listing, pk=self.kwargs["listing_id"])
        if bid_form.is_valid():
            bid_amount = bid_form.cleaned_data["bid"]
            return self.update_bid(request, bid_amount, listing, bid_form)
        return HttpResponseRedirect(reverse("bid", args=(listing.id,)))

    def update_bid(self, request, bid_amount, listing, bid_form):
        """
        update_bid() checks conditions of allowing bids and render if error
        message if bid is not allow
        """
        user_bid = listing.bids.filter(user=request.user).first()
        error_clean_bid = False
        wait_for_three_min = False
        if user_bid is None:
            error_clean_bid = self.place_bid(request, bid_amount, listing,
                                             datetime.now(timezone.utc))
        else:
            delta = datetime.now(timezone.utc) - user_bid.date
            if delta > timedelta(minutes=1):
                error_clean_bid = self.place_bid(request, bid_amount, listing,
                                                 datetime.now(timezone.utc))
            else:
                wait_for_three_min = True
        return render(request, "auctions/bid.html", {
            "listing": listing,
            "bid_form": bid_form,
            "wait_for_three_min": wait_for_three_min,
            "error_clean_bid": error_clean_bid,
            "comment_form": CommentForm(),
            "bid_count": listing.bids.all().count()
        })

    def place_bid(self, request, bid_amount, listing, current_time):
        """
        place_bid() update the bids to the database
        """
        settings.minutes = 1
        if bid_amount - listing.current_price() >= settings.minutes:
            error_clean_bid = False
            listing.bids.update(date=current_time)
            recent_bid = Bid.objects.create(date=current_time, listing=listing,
                                            bid=bid_amount, user=request.user)
            Listing.objects.filter(pk=self.kwargs["listing_id"]).update(
                winning_bid=recent_bid.id)
        else:
            error_clean_bid = True
        return error_clean_bid


def index(request):
    """Active listing tab, render all listings that are open"""
    listings = Listing.objects.filter(open_at=True)
    get_client_ip(request)
    return render(request, "auctions/index.html", {"listings": listings})


def hot_listing_view(request):
    """Qualified for HOT listing should to more than 5 bids"""
    settings.allow_hot_listing = 5
    for listing in Listing.objects.all():
        if listing.bids.all().count() > settings.allow_hot_listing:
            Listing.objects.filter(pk=listing.id).update(hot=True)
    # HOT listing tab, rendering html
    listings = Listing.objects.filter(hot=True, open_at=True)
    return render(request, "auctions/hot_listing.html", {"listings": listings})


def auto_close_listing() -> None:
    """Automatic closing system for listing"""
    current_date = datetime.now(timezone.utc).date()
    for listing in Listing.objects.all():
        if listing.end_date == current_date:
            Listing.objects.filter(pk=listing.id).update(open_at=False)


def search(request):
    """Search bar on index.html(Active Listing)"""
    value = request.GET.get('q', '')
    if Listing.objects.filter(title=str(value)).first() is not None:
        return HttpResponseRedirect(reverse("index"))
    sub_string_listings = []
    for listing in Listing.objects.all():
        if value.upper() in listing.title.upper():
            sub_string_listings.append(listing)
    return render(request, "auctions/index.html", {
        "search_listings": sub_string_listings,
        "search": True,
        "value": value
    })


def category_view(request):
    """Category tab, rendering html"""
    return render(request, "auctions/category.html", {
        "categories": Category.objects.all()
    })


def each_category_listing(request, category_id):
    """Render category list, Category tab"""
    return render(request, "auctions/each_category.html", {
        "listings": Listing.objects.filter(category=category_id, open_at=True)
    })


@login_required(login_url=LOGIN_URL)
def get_client_ip(request):
    """Get IP"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    User.objects.filter(pk=request.user.id).update(ip=ip)
    return block_ip_address(request, ip)


@login_required(login_url=LOGIN_URL)
def block_ip_address(request, ip):
    # Block IP address
    blocked_ip = ['78.46.163.212']
    for i in range(len(blocked_ip)):
        if ip == blocked_ip[i]:
            logout(request)
            return HttpResponse("You're not allow on the site")
    return HttpResponseRedirect(reverse("index"))


@login_required(login_url=LOGIN_URL)
def own_listing(request):
    """The listing that user post, Own Listing tab"""
    listings = Listing.objects.filter(owner=request.user)
    return render(request, "auctions/own_listing.html", {"listings": listings})


@login_required(login_url=LOGIN_URL)
def flag_listing(request, listing_id):
    """Report button on listing"""
    listing = get_object_or_404(Listing, pk=listing_id)
    if listing.owner == request.user:
        return HttpResponseRedirect(reverse("bid", args=(listing.id,)))
    if listing.flags.filter().first() is None:
        Flag.objects.create(flag_count=1, listing=listing, user=request.user)
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
            listing = get_object_or_404(Listing, pk=listing_id)
            Comment.objects.create(user=request.user, comment=clean_comment,
                                   listing=listing)
    return HttpResponseRedirect(reverse("bid", args=(listing.id,)))


@login_required(login_url=LOGIN_URL)
def watchlist(request, listing_id):
    """Add on watch list, when watch list button is click"""
    if request.method == "POST":
        listing = get_object_or_404(Listing, pk=listing_id)
        request.user.watch_listing.add(listing)
        return HttpResponseRedirect(reverse("watchlist_view"))
    return render(request, "auctions/watchlist.html")


@login_required(login_url=LOGIN_URL)
def remove_watchlist(request, listing_id):
    """Remove on watch list, when remove watch list button is click"""
    if request.method == "POST":
        listing = get_object_or_404(Listing, pk=listing_id)
        request.user.watch_listing.remove(listing)
        return HttpResponseRedirect(reverse("watchlist_view"))
    return render(request, "auctions/watchlist.html")


@login_required(login_url=LOGIN_URL)
def watchlist_view(request):
    """Render watch listing for user, Watch List tab"""
    user_watch_listing = request.user.watch_listing.all().filter(open_at=True)
    return render(request, "auctions/watchlist.html", {
        "user_watch_listing": user_watch_listing
    })


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
    get_client_ip(request)
    # First time when user visit the page
    if Category.objects.exists() is False:
        default_category = ["Programming", "Fashion", "Christmas",
                            "Electronics", "Property", "Sport", "Other"]
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
            image_two = form.cleaned_data["image_two"]
            image_three = form.cleaned_data["image_three"]
            starting_price = form.cleaned_data["starting_price"]
            if str(title.lower()) in spam or str(description.lower()) in spam:
                spam_word_error = True
            else:
                Listing.objects.create(title=title, description=description,
                                       category=category, image=image,
                                       image_two=image_two,
                                       image_three=image_three,
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
