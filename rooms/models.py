
from django.db import models


class Room(models.Model):

    ROOM_TYPES = [

        ('Single', 'Single'),

        ('Double', 'Double'),

        ('Deluxe', 'Deluxe'),

        ('Suite', 'Suite'),

    ]

    room_number = models.CharField(max_length=10, unique=True)

    room_type = models.CharField(
        max_length=20,
        choices=ROOM_TYPES
    )

    price = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )

    capacity = models.PositiveIntegerField()

    description = models.TextField()

    image = models.ImageField(
        upload_to='rooms/'
    )

    available = models.BooleanField(default=True)

    # def __str__(self):
    #     return self.room_number

    def __str__(self):
        return f"Room {self.room_number} - {self.room_type}"