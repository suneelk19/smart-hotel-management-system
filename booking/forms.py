from django import forms
from .models import Booking


class BookingForm(forms.ModelForm):

    class Meta:
        model = Booking

        # User aur Status ko form se hata diya
        fields = [
            "room",
            "check_in",
            "check_out",
            "adults",
            "children",
        ]

        widgets = {

            # Room Dropdown
            "room": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            # Check-in Date
            "check_in": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date"
                }
            ),

            # Check-out Date
            "check_out": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date"
                }
            ),

            # Adults
            "adults": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "1"
                }
            ),

            # Children
            "children": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0"
                }
            ),

        }

    # Form Validation
    def clean(self):

        cleaned_data = super().clean()

        room = cleaned_data.get("room")
        check_in = cleaned_data.get("check_in")
        check_out = cleaned_data.get("check_out")

        # Check-out validation
        if check_in and check_out:

            if check_out <= check_in:

                raise forms.ValidationError(
                    "Check-out date must be after Check-in date."
                )

        # Double booking validation
        if room and check_in and check_out:

            booking_exists = Booking.objects.filter(
                room=room,
                check_in__lt=check_out,
                check_out__gt=check_in,
                status__in=["Pending", "Approved", "Confirmed"]
            ).exists()

            if booking_exists:

                raise forms.ValidationError(
                    "This room is already booked for the selected dates."
                )

        return cleaned_data