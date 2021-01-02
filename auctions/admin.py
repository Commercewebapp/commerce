from django.contrib import admin

from .models import Listing, Bid

class ListingAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "description")


class BidAdmin(admin.ModelAdmin):
    list_display = ("id", "bid")


admin.site.register(Listing, ListingAdmin)
admin.site.register(Bid, BidAdmin)
