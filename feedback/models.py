

from django.db import models
from django.contrib.auth.models import User


class Feedback(models.Model):

    RATING_CHOICES = [
        (1, "1 Star"),
        (2, "2 Stars"),
        (3, "3 Stars"),
        (4, "4 Stars"),
        (5, "5 Stars"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    subject = models.CharField(
        max_length=100
    )

    message = models.TextField()

    rating = models.IntegerField(
        choices=RATING_CHOICES,
        default=5
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.subject}"