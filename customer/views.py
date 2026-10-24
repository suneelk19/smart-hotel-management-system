from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages

from booking.models import Booking
from payments.models import Payment
from payments.utils import send_payment_received_email
from feedback.models import Feedback

from .models import CustomerProfile, Notification
from .forms import CustomerProfileForm, EditProfileForm
from decimal import Decimal


# =====================================================
# Customer Dashboard
# =====================================================

@login_required
@user_passes_test(lambda u: not u.is_staff, login_url="home")
def customer_dashboard(request):

    bookings = Booking.objects.filter(user=request.user)
    payments = Payment.objects.filter(booking__user=request.user)
    notifications = Notification.objects.filter(
        customer=request.user
    ).order_by("-created_at")[:5]

    context = {

        "total_bookings": bookings.count(),

        "pending_bookings": bookings.filter(
            status="Pending"
        ).count(),

        "approved_bookings": bookings.filter(
            status="Approved"
        ).count(),

        "confirmed_bookings": bookings.filter(
            status="Confirmed"
        ).count(),

        "rejected_bookings": bookings.filter(
            status="Rejected"
        ).count(),

        "cancelled_bookings": bookings.filter(
            status="Cancelled"
        ).count(),

        "total_payments": payments.count(),

        "recent_bookings": bookings.order_by("-id")[:5],

        "recent_payments": payments.order_by("-id")[:5],

        "notifications": notifications,

    }

    return render(
        request,
        "customer/customer_dashboard.html",
        context
    )


# =====================================================
# Customer Profile
# =====================================================

@login_required
@user_passes_test(lambda u: not u.is_staff, login_url="home")
def my_profile(request):

    profile, created = CustomerProfile.objects.get_or_create(
        user=request.user
    )

    return render(
        request,
        "customer/profile.html",
        {
            "profile": profile
        }
    )


# =====================================================
# Edit Profile
# =====================================================

@login_required
@user_passes_test(lambda u: not u.is_staff, login_url="home")
def edit_profile(request):

    profile, created = CustomerProfile.objects.get_or_create(
        user=request.user
    )

    if request.method == "POST":

        user_form = EditProfileForm(
            request.POST,
            instance=request.user
        )

        profile_form = CustomerProfileForm(
            request.POST,
            request.FILES,
            instance=profile
        )

        if user_form.is_valid() and profile_form.is_valid():

            user_form.save()
            profile_form.save()

            messages.success(
                request,
                "Profile Updated Successfully."
            )

            return redirect("my_profile")

    else:

        user_form = EditProfileForm(
            instance=request.user
        )

        profile_form = CustomerProfileForm(
            instance=profile
        )

    return render(
        request,
        "customer/edit_profile.html",
        {
            "user_form": user_form,
            "profile_form": profile_form,
        }
    )


# =====================================================
# My Bookings
# =====================================================

@login_required
@user_passes_test(lambda u: not u.is_staff, login_url="home")
def my_bookings(request):

    bookings = Booking.objects.filter(
        user=request.user
    ).order_by("-id")

    return render(
        request,
        "customer/my_bookings.html",
        {
            "bookings": bookings
        }
    )


# =====================================================
# Booking Details
# =====================================================

@login_required
@user_passes_test(lambda u: not u.is_staff, login_url="home")
def booking_detail(request, pk):

    booking = get_object_or_404(
        Booking,
        id=pk,
        user=request.user
    )

    return render(
        request,
        "customer/booking_detail.html",
        {
            "booking": booking
        }
    )


# =====================================================
# My Payments
# =====================================================

@login_required
@user_passes_test(lambda u: not u.is_staff, login_url="home")
def my_payments(request):

    payments = Payment.objects.filter(
        booking__user=request.user
    ).order_by("-id")

    return render(
        request,
        "customer/my_payments.html",
        {
            "payments": payments
        }
    )


# =====================================================
# Notifications
# =====================================================

@login_required
@user_passes_test(lambda u: not u.is_staff, login_url="home")
def my_notifications(request):

    notifications = Notification.objects.filter(
        customer=request.user
    ).order_by("-created_at")

    return render(
        request,
        "customer/notifications.html",
        {
            "notifications": notifications
        }
    )


# =====================================================
# My Feedback
# =====================================================

@login_required
@user_passes_test(lambda u: not u.is_staff, login_url="home")
def my_feedback(request):

    feedbacks = Feedback.objects.filter(
        user=request.user
    ).order_by("-id")

    return render(
        request,
        "customer/feedback.html",
        {
            "feedbacks": feedbacks
        }
    )

# =====================================================
# Make Payment
# =====================================================

# @login_required
# @user_passes_test(lambda u: not u.is_staff, login_url="home")
# def make_payment(request, booking_id):

#     booking = get_object_or_404(
#         Booking,
#         id=booking_id,
#         user=request.user
#     )

#     if Payment.objects.filter(booking=booking, status="Paid").exists():
#         messages.info(request, "This booking is already paid.")
#         return redirect("booking_detail", pk=booking.id)

#     days = (booking.check_out - booking.check_in).days
#     if days <= 0:
#         days = 1
#     total_amount = booking.room.price * days

#     if request.method == "POST":
#         payment_method = request.POST.get("payment_method", "Credit Card")

#         payment = Payment.objects.create(
#             booking=booking,
#             amount=total_amount,
#             payment_method=payment_method,
#             status="Paid"
#         )

#         # Send "Payment Received / Booking Under Review" email (NO PDF yet)
#         send_payment_received_email(
#             customer_email=request.user.email,
#             customer_name=(f"{request.user.first_name} {request.user.last_name}".strip()
#                         or request.user.username),
#             booking_id=booking.id,
#             room=booking.room.room_number,
#             check_in=booking.check_in,
#             check_out=booking.check_out,
#             guests=booking.adults + booking.children,
#             amount=total_amount,
#             payment_method=payment_method,
#         )

#         messages.success(
#             request,
#             "Payment successful! Your booking request is under review. "
#             "You will receive a confirmation email once approved."
#         )
#         return redirect("my_payments")

#     return render(
#         request,
#         "customer/make_payment.html",
#         {
#             "booking": booking,
#             "total_amount": total_amount,
#             "days": days
#         }
#     )




# =====================================================
# Make Payment - Razorpay + Cash at Counter
# =====================================================

@login_required
@user_passes_test(lambda u: not u.is_staff, login_url="home")
def make_payment(request, booking_id):

    booking = get_object_or_404(
        Booking,
        id=booking_id,
        user=request.user
    )

    # Payment is allowed only after admin approval
    if booking.status != "Approved":
        messages.warning(
            request,
            "Payment is available only after your booking is approved."
        )
        return redirect("booking_detail", pk=booking.id)

    # Calculate the amount on the server
    days = (booking.check_out - booking.check_in).days

    if days <= 0:
        messages.error(
            request,
            "Invalid booking dates. Please contact hotel staff."
        )
        return redirect("booking_detail", pk=booking.id)

    total_amount = (
         Decimal(str(booking.room.price)) * days
    )   .quantize(Decimal("0.01"))

    if total_amount <= 0:
        messages.error(
            request,
            "Invalid room price. Please contact hotel staff."
        )
        return redirect("booking_detail", pk=booking.id)

    # Already-paid bookings cannot be paid again
    if Payment.objects.filter(
        booking=booking,
        status="Paid"
    ).exists():
        messages.info(
            request,
            "This booking is already paid."
        )
        return redirect("my_payments")

    if request.method == "POST":

        payment_method = request.POST.get(
            "payment_method", ""
        ).strip()

        online_methods = [
            "UPI",
            "Credit Card",
            "Debit Card",
            "Net Banking",
        ]

        # Cash payment: create or reuse a Pending record
        if payment_method == "Cash":

            cash_payment = Payment.objects.filter(
                booking=booking,
                payment_method="Cash",
                status="Pending"
            ).order_by("-id").first()

            if cash_payment:
                # Correct the amount if an older pending record
                # has an incorrect amount.
                cash_payment.amount = total_amount
                cash_payment.save(update_fields=["amount"])
            else:
                Payment.objects.create(
                    booking=booking,
                    amount=total_amount,
                    payment_method="Cash",
                    status="Pending"
                )

            messages.info(
                request,
                f"Cash payment of ₹{total_amount} is pending. "
                "Please pay at the hotel counter. "
                "Staff will mark it as Paid after receiving the cash."
            )

            return redirect("my_payments")

        # Online payment remains handled by Razorpay
        if payment_method in online_methods:
            return redirect(
                "razorpay_create_order",
                booking_id=booking.id
            )

        messages.error(
            request,
            "Please select a valid payment method."
        )

    return render(
        request,
        "customer/make_payment.html",
        {
            "booking": booking,
            "total_amount": total_amount,
            "days": days,
        }
    )



# =====================================================
# Make Payment - Razorpay + Cash at Counter
# =====================================================

# @login_required
# @user_passes_test(lambda u: not u.is_staff, login_url="home")
# def make_payment(request, booking_id):

#     booking = get_object_or_404(
#         Booking,
#         id=booking_id,
#         user=request.user
#     )

#     # Payment is allowed only after admin approval
#     if booking.status != "Approved":
#         messages.warning(
#             request,
#             "Payment is available only after your booking is approved."
#         )
#         return redirect("booking_detail", pk=booking.id)

#     # Do not allow a second payment for an already-paid booking
#     if Payment.objects.filter(
#         booking=booking,
#         status="Paid"
#     ).exists():
#         messages.info(
#             request,
#             "This booking is already paid."
#         )
#         return redirect("my_payments")

#     days = (booking.check_out - booking.check_in).days

#     if days <= 0:
#         messages.error(
#             request,
#             "Invalid booking dates. Please contact hotel staff."
#         )
#         return redirect("booking_detail", pk=booking.id)

#     total_amount = booking.room.price * days

#     if request.method == "POST":

#         payment_method = request.POST.get("payment_method", "").strip()

#         online_methods = [
#             "UPI",
#             "Credit Card",
#             "Debit Card",
#             "Net Banking",
#         ]

#         # Cash is handled separately: payment remains Pending
#         if payment_method == "Cash":

#             cash_payment = Payment.objects.filter(
#                 booking=booking,
#                 payment_method="Cash",
#                 status="Pending"
#             ).first()

#             if not cash_payment:
#                 Payment.objects.create(
#                     booking=booking,
#                     amount=total_amount,
#                     payment_method="Cash",
#                     status="Pending"
#                 )

#             messages.info(
#                 request,
#                 "Cash payment selected. Please pay at the hotel counter. "
#                 "Your payment will remain pending until staff confirms it."
#             )

#             return redirect("my_payments")

#         # Online methods must go through Razorpay
#         if payment_method in online_methods:
#             return redirect(
#                 "razorpay_create_order",
#                 booking_id=booking.id
#             )

#         messages.error(
#             request,
#             "Please select a valid payment method."
#         )

#     return render(
#         request,
#         "customer/make_payment.html",
#         {
#             "booking": booking,
#             "total_amount": total_amount,
#             "days": days
#         }
#     )