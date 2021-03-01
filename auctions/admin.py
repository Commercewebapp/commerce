from django.contrib import admin

from .models import Listing, Category, User, Comment, Bid, Flag


class ListingAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "category", "starting_price", "open_at", "winning_bid", "owner")


class BidAdmin(admin.ModelAdmin):
    list_display = ("id", "date", "listing", "bid", "user")


class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "comment", "listing")


class FlagAdmin(admin.ModelAdmin):
    list_display = ("id", "flag", "listing", "user")


admin.site.register(Listing, ListingAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(User)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(Flag, FlagAdmin)
