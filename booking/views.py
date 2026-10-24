from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test

from .models import Booking
from .forms import BookingForm

from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib import messages
import csv

from payments.utils import send_booking_email, send_booking_rejected_email
from payments.models import Payment
from django.http import HttpResponse
from django.shortcuts import redirect


# =====================================
# Booking List
# =====================================
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_staff, login_url="home")
def booking_list(request):

    query = request.GET.get("q", "")

    bookings = Booking.objects.all()

    if query:

        bookings = bookings.filter(
            Q(user__username__icontains=query) |
            Q(room__room_number__icontains=query) |
            Q(status__icontains=query)
        )

    paginator = Paginator(bookings, 5)

    page_number = request.GET.get("page")

    bookings = paginator.get_page(page_number)

    return render(
        request,
        "booking_list.html",
        {
            "bookings": bookings,
            "query": query,
        }
    )




@login_required(login_url="login")
def add_booking(request):

    if request.method == "POST":

        form = BookingForm(request.POST)

        if form.is_valid():

            booking = form.save(commit=False)

            booking.user = request.user

            # ---------------------------------------
            # Check if room is already booked
            # ---------------------------------------

            room_already_booked = Booking.objects.filter(
                room=booking.room,
                status__in=["Pending", "Approved", "Confirmed"],
                check_in__lt=booking.check_out,
                check_out__gt=booking.check_in
            ).exists()

            if room_already_booked:

                messages.error(
                    request,
                    "This room is already booked for the selected dates."
                )

                return render(
                    request,
                    "add_booking.html",
                    {
                        "form": form
                    }
                )

            booking.user = request.user
            booking.status = "Pending"
            booking.save()

            messages.success(
                request,
                "Booking Added Successfully."
            )

            return redirect("booking_list")

    else:

        initial_data = {}
        room_id = request.GET.get("room")
        check_in = request.GET.get("check_in", "")
        check_out = request.GET.get("check_out", "")
        if room_id:
            initial_data["room"] = room_id
        if check_in:
            initial_data["check_in"] = check_in
        if check_out:
            initial_data["check_out"] = check_out

        form = BookingForm(initial=initial_data)

    return render(
        request,
        "add_booking.html",
        {
            "form": form
        }
    )



# =====================================
# Edit Booking
# =====================================
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_staff, login_url="home")
def edit_booking(request, pk):

    booking = get_object_or_404(
        Booking,
        pk=pk
    )

    if request.method == "POST":

        form = BookingForm(
            request.POST,
            instance=booking
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Booking Updated Successfully."
            )

            return redirect("booking_list")

    else:

        form = BookingForm(
            instance=booking
        )

    return render(
        request,
        "edit_booking.html",
        {
            "form": form,
            "booking": booking
        }
    )


# =====================================
# Delete Booking
# =====================================
# @login_required(login_url="login")
# def delete_booking(request, pk):

#     booking = get_object_or_404(
#         Booking,
#         pk=pk
#     )

#     # Room Available Again
#     booking.room.available = True
#     booking.room.save()

#     booking.delete()

#     messages.success(
#         request,
#         "Booking Deleted Successfully."
#     )

#     return redirect("booking_list")



@login_required(login_url="login")
@user_passes_test(lambda u: u.is_staff, login_url="home")
def delete_booking(request, pk):

    booking = get_object_or_404(
        Booking,
        pk=pk
    )

    booking.room.available = True
    booking.room.save()

    booking.delete()

    messages.success(
        request,
        "Booking Deleted Successfully."
    )

    return redirect("booking_list")




@login_required(login_url="login")
@user_passes_test(lambda u: u.is_staff, login_url="home")
def approve_booking(request, pk):

    booking = get_object_or_404(
        Booking,
        pk=pk
    )

    booking.status = "Approved"
    booking.save()

    # Room ko occupied bana do
    booking.room.available = False
    booking.room.save()

    # Send Booking Confirmed email with PDF receipt
    payment = booking.payments.filter(status="Paid").first()
    amount = payment.amount if payment else 0
    payment_method = payment.payment_method if payment else "N/A"

    send_booking_email(
        customer_email=booking.user.email,
        customer_name=booking.user.get_full_name() or booking.user.username,
        booking_id=booking.id,
        room=booking.room.room_number,
        check_in=booking.check_in,
        check_out=booking.check_out,
        guests=booking.adults + booking.children,
        amount=amount,
        payment_status="Paid",
        payment_method=payment_method,
    )

    messages.success(
        request,
        "Booking Approved. Confirmation email with PDF receipt sent to customer."
    )

    return redirect("booking_list")




@login_required(login_url="login")
@user_passes_test(lambda u: u.is_staff, login_url="home")
def reject_booking(request, pk):

    booking = get_object_or_404(
        Booking,
        pk=pk
    )

    booking.status = "Rejected"
    booking.save()

    booking.room.available = True
    booking.room.save()

    # Send Booking Rejected email
    send_booking_rejected_email(
        customer_email=booking.user.email,
        customer_name=booking.user.get_full_name() or booking.user.username,
        booking_id=booking.id,
        room=booking.room.room_number,
        check_in=booking.check_in,
        check_out=booking.check_out,
    )

    messages.warning(
        request,
        "Booking Rejected. Rejection email sent to customer."
    )

    return redirect("booking_list")


# =====================================
# Export CSV
# =====================================
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_staff, login_url="home")
def export_booking_csv(request):

    response = HttpResponse(
        content_type="text/csv"
    )

    response["Content-Disposition"] = (
        'attachment; filename="bookings.csv"'
    )

    writer = csv.writer(response)

    writer.writerow([
        "Customer",
        "Room",
        "Check In",
        "Check Out",
        "Adults",
        "Children",
        "Status"
    ])

    bookings = Booking.objects.all()

    for booking in bookings:

        writer.writerow([
            booking.user.username,
            booking.room.room_number,
            booking.check_in,
            booking.check_out,
            booking.adults,
            booking.children,
            booking.status,
        ])

    return response