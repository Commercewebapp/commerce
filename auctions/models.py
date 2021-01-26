from django.contrib.auth.models import AbstractUser
from django.db import models


class Comment(models.Model):
    user = models.ForeignKey("User", on_delete=models.DO_NOTHING)
    comment = models.TextField()
    listing_title = models.ForeignKey("Listing", default=None,
                                      on_delete=models.DO_NOTHING,
                                      related_name="listing_com")

    def __str__(self):
        return f"{self.user}, Comment: {self.comment}"


class Category(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.name}"


class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField()
    image = models.ImageField(upload_to="listing_images", default=None)
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)
    create_at = models.DateTimeField(auto_now_add=True)
    open_at = models.BooleanField()
    owner = models.ForeignKey("User", on_delete=models.DO_NOTHING)
    starting_price = models.DecimalField(decimal_places=2, max_digits=8,
                                         null=True)

    def __str__(self):
        return f"{self.title}"


class User(AbstractUser):
    watch_listing = models.ManyToManyField(Listing)


class Bid(models.Model):
    date = models.DateTimeField(null=True)
    listing = models.ForeignKey(Listing, on_delete=models.DO_NOTHING,
                                related_name="listing_bid")
    track_user = models.ForeignKey("User", on_delete=models.DO_NOTHING)

    def __str__(self):
        return f"{self.date}"
