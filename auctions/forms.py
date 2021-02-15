from django import forms
from .models import Listing, Bid, Comment
from django.forms import ModelForm


class CreateListing(ModelForm):
    class Meta:
        model = Listing
        fields = ["title", "description", "image", "category", "starting_price",
                  "end_date"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control col-md-8 col-md-lg-8"}),
            "description": forms.Textarea(attrs={"class": "form-control col-md-8 col-lg-8", "rows": 10})
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
            "comment": forms.Textarea(attrs={"class": "form-control col-md-5 col-lg-5", "rows": 5})
        }
