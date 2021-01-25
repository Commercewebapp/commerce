from django.contrib import admin

from .models import Listing, Category, User, Comment, Bid


class ListingAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "description", "category_id", "owner")


class BidAdmin(admin.ModelAdmin):
    list_display = ("id", "date", "listing", "track_user")


class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "comment", "listing_title")


admin.site.register(Listing, ListingAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(User)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Bid, BidAdmin)
