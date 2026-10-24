from django import forms
from .models import Payment


class PaymentForm(forms.ModelForm):

    class Meta:
        model = Payment

        fields = "__all__"

        widgets = {

            "booking": forms.Select(
                attrs={"class": "form-select"}
            ),

            "amount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01"
                }
            ),

            "payment_method": forms.Select(
                attrs={"class": "form-select"}
            ),

            "payment_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date"
                }
            ),

            "status": forms.Select(
                attrs={"class": "form-select"}
            ),

        }