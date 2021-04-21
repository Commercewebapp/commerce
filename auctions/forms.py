from datetime import datetime, timezone, timedelta

from django import forms
from django.forms import ModelForm

from .models import Listing, Bid, Comment


class CreateListing(ModelForm):
    class Meta:
        tomorrow_date = datetime.now(timezone.utc) + timedelta(days=1)
        model = Listing
        fields = [
            "title",
            "description",
            "image",
            "image_two",
            "image_three",
            "category",
            "starting_price",
            "end_date",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control col-md-8 col-md-lg-8"}
            ),
            "description": forms.Textarea(
                attrs={"class": "form-control col-md-8 col-lg-8", "rows": 10}
            ),
            "end_date": forms.TextInput(
                attrs={"placeholder": tomorrow_date.date}
            ),
        }


class BidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ["bid"]


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ["comment"]
        widgets = {
            "comment": forms.Textarea(
                attrs={"class": "form-control col-md-5 col-lg-5", "rows": 5}
            )
        }
