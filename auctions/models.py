from django.contrib.auth.models import AbstractUser
from django.db import models


class Comment(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    comment = models.TextField()
    listing = models.ForeignKey("Listing", default=None,
                                on_delete=models.CASCADE,
                                related_name="comment")

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
    open_at = models.BooleanField(null=True, default=True)
    owner = models.ForeignKey("User", on_delete=models.CASCADE)
    starting_price = models.DecimalField(decimal_places=2, max_digits=8)

    def winning_bid(self):
        return self.bid.order_by("-date").first()

    def __str__(self):
        return f"{self.title}"


class User(AbstractUser):
    watch_listing = models.ManyToManyField(Listing)


class Bid(models.Model):
    date = models.DateTimeField(null=True)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE,
                                related_name="bid")
    user = models.ForeignKey("User", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.date}"
