from django.contrib.auth.models import AbstractUser
from django.db import models


class Comment(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    comment = models.TextField()
    listing = models.ForeignKey("Listing", default=None,
                                on_delete=models.CASCADE,
                                related_name="comment")
    comment_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.user} -> {self.comment}"


class Category(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.name}"


class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField()
    image = models.ImageField(upload_to="listing_images", default=None)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)
    create_at = models.DateTimeField(auto_now_add=True)
    open_at = models.BooleanField(null=True, default=True)
    owner = models.ForeignKey("User", on_delete=models.CASCADE)
    starting_price = models.DecimalField(decimal_places=2, max_digits=8)
    winning_bid = models.ForeignKey("Bid", on_delete=models.CASCADE,
                                    related_name="won", null=True)

    def current_price(self):
        highest = self.bids.order_by("-bid").first()
        if highest is None:
            return self.starting_price
        return highest.bid

    def __str__(self):
        return f"{self.title} ({self.owner}) ({self.current_price()})"


class User(AbstractUser):
    watch_listing = models.ManyToManyField(Listing)


class Bid(models.Model):
    date = models.DateTimeField(null=True)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE,
                                related_name="bids")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bid = models.DecimalField(decimal_places=2, max_digits=8, null=True)

    def __str__(self):
        return f"{self.date} ({self.user}) ({self.listing.current_price()})"


class Flag(models.Model):
    flag_count = models.IntegerField(null=True)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE,
                                related_name="flags", null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True,
                             related_name="flags_user")

    def __str__(self):
        return f"{self.listing}: {self.flag_count} {self.user}"
