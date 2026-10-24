from django.urls import path
from . import views

urlpatterns = [

    # ===========================
    # Customer Dashboard
    # ===========================

    path(
        "dashboard/",
        views.customer_dashboard,
        name="customer_dashboard",
    ),

    # ===========================
    # Profile
    # ===========================

    path(
        "profile/",
        views.my_profile,
        name="my_profile",
    ),

    path(
        "profile/edit/",
        views.edit_profile,
        name="edit_profile",
    ),

    # ===========================
    # Bookings
    # ===========================

    path(
        "bookings/",
        views.my_bookings,
        name="my_bookings",
    ),

    path(
        "booking/<int:pk>/",
        views.booking_detail,
        name="booking_detail",
    ),

    # ===========================
    # Payments
    # ===========================

    path(
        "payments/",
        views.my_payments,
        name="my_payments",
    ),

    path(
        "payment/<int:booking_id>/",
        views.make_payment,
        name="make_payment",
    ),

    # ===========================
    # Notifications
    # ===========================

    path(
        "notifications/",
        views.my_notifications,
        name="my_notifications",
    ),

    # ===========================
    # Feedback
    # ===========================

    path(
        "feedback/",
        views.my_feedback,
        name="my_feedback",
    ),

]