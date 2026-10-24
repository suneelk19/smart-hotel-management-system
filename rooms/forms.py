from django import forms
from .models import Room


class RoomForm(forms.ModelForm):

    class Meta:
        model = Room

        fields = "__all__"

        widgets = {

            "room_number": forms.TextInput(
                attrs={"class": "form-control"}
            ),

            "room_type": forms.TextInput(
                attrs={"class": "form-control"}
            ),

            "price": forms.NumberInput(
                attrs={"class": "form-control"}
            ),

            "available": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),

        }