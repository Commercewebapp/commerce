from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    title = models.CharField(max_length=150)
    bid = models.IntegerField()
    description = models.CharField(max_length=500)
