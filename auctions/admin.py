from django.contrib import admin

from .models import Listing, Category, User, Comment, BidTimer


class ListingAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "description", "category_id", "owner")


class BidAdmin(admin.ModelAdmin):
    list_display = ("id", "listing_id", "bid", "user")


class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "comment", "listing_title")


class BidTimerAdmin(admin.ModelAdmin):
    list_display = ("id", "user_place_at_bid", "listing")


admin.site.register(Listing, ListingAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(User)
admin.site.register(Comment, CommentAdmin)
admin.site.register(BidTimer, BidTimerAdmin)
