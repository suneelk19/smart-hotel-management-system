from django import forms
from django.contrib.auth.models import User
from .models import CustomerProfile, Notification


class CustomerProfileForm(forms.ModelForm):
    class Meta:
        model = CustomerProfile
        fields = [
            "phone",
            "address",
            "city",
            "state",
            "country",
            "pincode",
            "profile_image",
        ]


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
        ]


class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = [
            "title",
            "message",
        ]