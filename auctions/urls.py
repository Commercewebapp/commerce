from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_listing", views.create_listing, name="create_listing"),
    path("<int:listing_id>", views.bid, name="bid"),
    path("watchlist/<int:listing_id>", views.watchlist, name="watchlist"),
    path("watchlistview", views.watchlistview, name="watchlistview")
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
