from django.db import models
from django.contrib.auth.models import User
from rooms.models import Room


class Booking(models.Model):

    STATUS = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE
    )

    check_in = models.DateField()

    check_out = models.DateField()

    adults = models.PositiveIntegerField()

    children = models.PositiveIntegerField(
        default=0
    )

    booking_date = models.DateTimeField(
        auto_now_add=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default='Pending'
    )

    class Meta:
        ordering = ['-booking_date']
        verbose_name = "Booking"
        verbose_name_plural = "Bookings"

    def __str__(self):
        return f"{self.user.username} - Room {self.room.room_number} ({self.status})"