from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_listing", views.create_listing, name="create_listing"),
    path("<int:listing_id>", views.BidView.as_view(), name="bid"),
    path("remove_watchlist/<int:listing_id>", views.remove_watchlist,
         name="remove_watchlist"),
    path("watchlist/<int:listing_id>", views.watchlist, name="watchlist"),
    path("close_bid/<int:listing_id>", views.close_bid, name="close_bid"),
    path("close_bid_view", views.close_bid_view, name="close_bid_view"),
    path("category_view", views.category_view, name="category_view"),
    path("each_category_listing/<int:category_id>", views.each_category_listing,
         name="each_category_listing"),
    path("comment/<int:listing_id>", views.comment, name="comment"),
    path("watchlist_view", views.watchlist_view, name="watchlist_view"),
    path("flag/<int:listing_id>", views.flag_listing, name="flag_listing"),
    path("own_listing", views.own_listing, name="own_listing"),
    path("search", views.search, name="search")
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
