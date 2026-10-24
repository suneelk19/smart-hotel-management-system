from django.db import models
from booking.models import Booking


class Report(models.Model):

    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE
    )

    generated_on = models.DateTimeField(
        auto_now_add=True
    )

    remarks = models.CharField(
        max_length=200,
        blank=True
    )

    def __str__(self):
        return self.booking.customer_name