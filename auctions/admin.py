from django.contrib import admin

from .models import Listing, Bid, Category


class ListingAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "description", "category_id")


class BidAdmin(admin.ModelAdmin):
    list_display = ("id", "listing_id", "bid", "user")


class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


admin.site.register(Listing, ListingAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(Category, CategoryAdmin)
