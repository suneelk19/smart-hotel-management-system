


from django import forms
from .models import Feedback


class FeedbackForm(forms.ModelForm):

    class Meta:
        model = Feedback

        fields = [
            "user",
            "subject",
            "message",
            "rating",
        ]

        widgets = {

            "user": forms.Select(
                attrs={"class": "form-select"}
            ),

            "subject": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Subject"
                }
            ),

            "message": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Write your feedback..."
                }
            ),

            "rating": forms.Select(
                attrs={"class": "form-select"}
            ),
        }