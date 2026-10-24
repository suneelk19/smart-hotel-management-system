
from django.db import models
from booking.models import Booking
import uuid


class Payment(models.Model):

    # Payment Status Choices
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Paid", "Paid"),
        ("Failed", "Failed"),
        ("Refunded", "Refunded"),
    ]

    # Payment Method Choices
    METHOD_CHOICES = [
        ("Cash", "Cash"),
        ("UPI", "UPI"),
        ("Credit Card", "Credit Card"),
        ("Debit Card", "Debit Card"),
        ("Net Banking", "Net Banking"),
        ("Razorpay", "Razorpay"),
    ]

    # Booking
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name="payments"
    )

    # Receipt Number
    receipt_number = models.CharField(
        max_length=30,
        unique=True,
        blank=True,
        null=True
    )

    # Amount
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    # Payment Method
    payment_method = models.CharField(
        max_length=20,
        choices=METHOD_CHOICES,
        default="Cash"
    )

    # Payment Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending"
    )

    # Payment Date
    payment_date = models.DateTimeField(
        auto_now_add=True
    )

    # Razorpay Integration Fields
    razorpay_order_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        unique=True
    )

    razorpay_payment_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        unique=True
    )

    class Meta:
        ordering = ["-payment_date"]

    def save(self, *args, **kwargs):
        if not self.receipt_number:
            self.receipt_number = (
                "REC-" + uuid.uuid4().hex[:8].upper()
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.receipt_number} - {self.booking.user.username}"




# ==========================================
# Refund Request Model
# ==========================================

class RefundRequest(models.Model):

    STATUS_CHOICES = [
        ("Requested", "Requested"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),
        ("Processing", "Processing"),
        ("Processed", "Processed"),
        ("Failed", "Failed"),
    ]

    payment = models.OneToOneField(
        Payment,
        on_delete=models.PROTECT,
        related_name="refund_request"
    )

    reason = models.TextField()

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Requested"
    )

    razorpay_refund_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        unique=True
    )

    admin_note = models.TextField(
        blank=True
    )

    requested_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    processed_at = models.DateTimeField(
        blank=True,
        null=True
    )

    class Meta:
        ordering = ["-requested_at"]

    def __str__(self):
        return (
            f"Refund for {self.payment.receipt_number} "
            f"- {self.status}"
        )
