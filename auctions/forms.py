from django import forms


class CreateListing(forms.Form):
    title = forms.CharField(label="Title", max_length=100,
                            widget=forms.TextInput(attrs={
                                "class": "form-control col-md-8 col-md-lg-8"
                            }))
    description = forms.CharField(label="Description", max_length=200,
                                  widget=forms.Textarea(attrs={
                                      "class": "form-control col-md-8 col-lg-8",
                                      "rows": 10
                                  }))
