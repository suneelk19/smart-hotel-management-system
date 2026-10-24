from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test

from rooms.models import Room
from booking.models import Booking
from payments.models import Payment
from feedback.models import Feedback
from staff.models import Staff


@login_required(login_url="login")
@user_passes_test(lambda u: u.is_staff, login_url="home")
def reports(request):

    context = {

        "total_rooms": Room.objects.count(),

        "available_rooms": Room.objects.filter(
            available=True
        ).count(),

        "total_bookings": Booking.objects.count(),

        "approved_bookings": Booking.objects.filter(
            status="Approved"
        ).count(),

        "pending_bookings": Booking.objects.filter(
            status="Pending"
        ).count(),

        "rejected_bookings": Booking.objects.filter(
            status="Rejected"
        ).count(),

        "total_payments": Payment.objects.count(),

        "total_feedback": Feedback.objects.count(),

        "total_staff": Staff.objects.count(),

        "total_customers": User.objects.count(),

    }

    return render(
        request,
        "reports.html",
        context
    )