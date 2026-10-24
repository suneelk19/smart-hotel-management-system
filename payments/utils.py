from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

from .pdf_generator import generate_receipt
from decimal import Decimal

from .models import Payment
from .pdf_generator import generate_receipt



# def send_booking_email(
#     customer_email,
#     customer_name,
#     booking_id,
#     room,
#     check_in,
#     check_out,
#     guests,
#     amount,
#     payment_status,
#     payment_method="Cash",
# ):

#     try:

#         print("=" * 50)
#         print("STEP 1 : Email Function Started")

#         subject = "🏨 Smart Hotel Booking Confirmation"

#         from_email = settings.EMAIL_HOST_USER

#         recipient_list = [customer_email]

#         print("STEP 2 : Rendering HTML")

#         html_content = render_to_string(
#             "emails/booking_email.html",
#             {
#                 "customer_name": customer_name,
#                 "booking_id": booking_id,
#                 "room": room,
#                 "check_in": check_in,
#                 "check_out": check_out,
#                 "guests": guests,
#                 "amount": amount,
#                 "payment_status": payment_status,
#                 "payment_method": payment_method,
#             }
#         )

#         print("STEP 3 : HTML Ready")

#         email = EmailMultiAlternatives(
#             subject,
#             "",
#             from_email,
#             recipient_list,
#         )

#         email.attach_alternative(
#             html_content,
#             "text/html"
#         )

#         print("STEP 4 : Generating PDF")

#         pdf = generate_receipt(
#             booking_id,
#             customer_name,
#             room,
#             check_in,
#             check_out,
#             guests,
#             amount,
#             payment_status,
#             payment_method,
#         )

#         print("STEP 5 : PDF Generated")

#         email.attach(
#             f"Booking_{booking_id}.pdf",
#             pdf,
#             "application/pdf",
#         )

#         print("STEP 6 : PDF Attached")

#         result = email.send()

#         print("=" * 50)
#         print("EMAIL SEND RESULT :", result)
#         print("[SUCCESS] EMAIL SENT SUCCESSFULLY")
#         print("=" * 50)

#     except Exception as e:

#         print("=" * 50)
#         print("[ERROR] EMAIL ERROR")
#         print("Error Type :", type(e).__name__)
#         print("Error Message :", e)
#         print("=" * 50)


def send_booking_email(
    customer_email,
    customer_name,
    booking_id,
    room,
    check_in,
    check_out,
    guests,
    amount,
    payment_status,
    payment_method="Cash",
):
    try:
        # Prefer the actual Paid payment stored in the database.
        paid_payment = (
            Payment.objects
            .filter(booking_id=booking_id, status="Paid")
            .order_by("-payment_date", "-id")
            .first()
        )

        if paid_payment:
            amount = paid_payment.amount

            # Use the saved payment details as the source of truth.
            payment_status = paid_payment.status
            payment_method = paid_payment.payment_method

        # Convert amount safely to Decimal and format to 2 decimal places.
        amount = Decimal(str(amount or "0")).quantize(
            Decimal("0.01")
        )

        print("BOOKING EMAIL DEBUG")
        print("Booking ID:", booking_id)
        print("Payment Amount:", amount)
        print("Payment Status:", payment_status)
        print("Payment Method:", payment_method)

        subject = "Smart Hotel Booking Confirmation"
        from_email = settings.EMAIL_HOST_USER

        html_content = render_to_string(
            "emails/booking_email.html",
            {
                "customer_name": customer_name,
                "booking_id": booking_id,
                "room": room,
                "check_in": check_in,
                "check_out": check_out,
                "guests": guests,
                "amount": amount,
                "payment_status": payment_status,
                "payment_method": payment_method,
            },
        )

        email = EmailMultiAlternatives(
            subject,
            "",
            from_email,
            [customer_email],
        )

        email.attach_alternative(html_content, "text/html")

        pdf = generate_receipt(
            booking_id,
            customer_name,
            room,
            check_in,
            check_out,
            guests,
            amount,
            payment_status,
            payment_method,
        )

        email.attach(
            f"Booking_{booking_id}.pdf",
            pdf,
            "application/pdf",
        )

        result = email.send()
        print("BOOKING EMAIL SEND RESULT:", result)

        return result

    except Exception as e:
        print(
            "[ERROR] BOOKING EMAIL ERROR:",
            type(e).__name__,
            str(e),
        )
        raise



# =====================================================
# Email: Payment Received / Booking Request Received
# (Sent after customer pays — NO PDF receipt yet)
# =====================================================

def send_payment_received_email(
    customer_email,
    customer_name,
    booking_id,
    room,
    check_in,
    check_out,
    guests,
    amount,
    payment_method,
):
    try:
        subject = "✅ Payment Received – Booking Under Review | Smart Hotel"
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [customer_email]

        html_content = render_to_string(
            "emails/payment_received_email.html",
            {
                "customer_name": customer_name,
                "booking_id": booking_id,
                "room": room,
                "check_in": check_in,
                "check_out": check_out,
                "guests": guests,
                "amount": amount,
                "payment_method": payment_method,
            }
        )

        email = EmailMultiAlternatives(
            subject, "", from_email, recipient_list
        )
        email.attach_alternative(html_content, "text/html")
        result = email.send()

        print("=" * 50)
        print("PAYMENT RECEIVED EMAIL SENT :", result)
        print("=" * 50)

    except Exception as e:
        print("=" * 50)
        print("[ERROR] PAYMENT RECEIVED EMAIL ERROR")
        print(type(e).__name__, e)
        print("=" * 50)


# =====================================================
# Email: Booking Rejected
# (Sent when admin rejects the booking)
# =====================================================

def send_booking_rejected_email(
    customer_email,
    customer_name,
    booking_id,
    room,
    check_in,
    check_out,
):
    try:
        subject = "❌ Booking Request Rejected | Smart Hotel"
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [customer_email]

        html_content = render_to_string(
            "emails/booking_rejected_email.html",
            {
                "customer_name": customer_name,
                "booking_id": booking_id,
                "room": room,
                "check_in": check_in,
                "check_out": check_out,
            }
        )

        email = EmailMultiAlternatives(
            subject, "", from_email, recipient_list
        )
        email.attach_alternative(html_content, "text/html")
        result = email.send()

        print("=" * 50)
        print("BOOKING REJECTED EMAIL SENT :", result)
        print("=" * 50)

    except Exception as e:
        print("=" * 50)
        print("[ERROR] BOOKING REJECTED EMAIL ERROR")
        print(type(e).__name__, e)
        print("=" * 50)