from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Category(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.name}"


class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField()
    image = models.ImageField(upload_to="listing_images", default=None, null=True)
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)
    create_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    open_at = models.BooleanField(default=True)
    owner = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    starting_price = models.DecimalField(decimal_places=2, max_digits=10, null=True)

    def __str__(self):
        return f"Title: {self.title}, Category: {self.category_id}"


class Bid(models.Model):
    listing_id = models.ForeignKey(Listing, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    bid = models.DecimalField(decimal_places=2, max_digits=10, null=True)
    bid_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"ID: {self.listing_id}, User: {self.user}, Bid: {self.bid}"
