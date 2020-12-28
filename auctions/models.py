from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class listings(models.Model):
    title = models.CharField(max_length=150)


class bids(models.Model):
    bid = models.IntegerField()


class comments(models.Model):
    description = models.CharField(max_length=500)
