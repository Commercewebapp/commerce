from django import forms
from .models import Category


class CreateListing(forms.Form):
    title = forms.CharField(max_length=64, widget=forms.TextInput(attrs={
        "class": "form-control col-md-8 col-md-lg-8"
    }))
    description = forms.CharField(max_length=200, widget=forms.Textarea(attrs={
        "class": "form-control col-md-8 col-lg-8", "rows": 10
    }))
    image = forms.ImageField()
    category = forms.ModelChoiceField(queryset=Category.objects.all())
    starting_price = forms.IntegerField()


class BidForm(forms.Form):
    bid_form = forms.IntegerField()


class CommentForm(forms.Form):
    comment_box = forms.CharField(max_length=200, widget=forms.Textarea(attrs={
        "class": "form-control col-md-5 col-lg-5", "rows": 5
    }))
