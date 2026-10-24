import json
from decimal import Decimal

import razorpay

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from payments.utils import send_booking_email
from booking.models import Booking



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q, Sum
from django.http import HttpResponse

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

from .models import Payment
from .forms import PaymentForm
from openpyxl import Workbook
from django.urls import reverse

from django.contrib import messages
from django.utils import timezone
from .models import Payment, RefundRequest

# ======================================
# PDF Report Imports
# ======================================

from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph
)

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from django.core.paginator import Paginator


# ==========================================
# Payment List
# ==========================================

@login_required(login_url="login")
@user_passes_test(lambda u: u.is_staff, login_url="home")
def payment_list(request):

    # Search Value
    query = request.GET.get("q", "")

    # Get All Payments
    payments = Payment.objects.all()

    # ======================================
    # Search Payments
    # ======================================
    if query:

        payments = payments.filter(

            Q(booking__user__username__icontains=query) |

            Q(payment_method__icontains=query) |

            Q(status__icontains=query)

        )

    # ======================================
    # Dashboard Cards (Pagination se pehle)
    # ======================================

    total_payments = payments.count()

    paid_payments = payments.filter(
        status="Paid"
    ).count()

    pending_payments = payments.filter(
        status="Pending"
    ).count()

    failed_payments = payments.filter(
        status="Failed"
    ).count()

    total_revenue = payments.filter(
        status="Paid"
    ).aggregate(
        Sum("amount")
    )["amount__sum"] or 0

    # ======================================
    # Pagination
    # 5 Records Per Page
    # ======================================

    paginator = Paginator(
        payments,
        5
    )

    page_number = request.GET.get("page")

    payments = paginator.get_page(page_number)

    # ======================================
    # Context
    # ======================================

    context = {

        "payments": payments,

        "query": query,

        "total_payments": total_payments,

        "paid_payments": paid_payments,

        "pending_payments": pending_payments,

        "failed_payments": failed_payments,

        "total_revenue": total_revenue,

    }

    return render(
        request,
        "payment_list.html",
        context
    )


# ==========================================
# Add Payment
# ==========================================
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_staff, login_url="home")
def add_payment(request):

    if request.method == "POST":

        form = PaymentForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect("payment_list")

    else:

        form = PaymentForm()

    return render(
        request,
        "add_payment.html",
        {
            "form": form
        }
    )




@login_required(login_url="login")
@user_passes_test(lambda u: u.is_staff, login_url="home")
def edit_payment(request, pk):

    payment = get_object_or_404(Payment, pk=pk)

    if request.method == "POST":

        old_status = payment.status
        form = PaymentForm(request.POST, instance=payment)

        if form.is_valid():

            payment = form.save(commit=False)
            booking = payment.booking

            # Calculate the correct amount from the booking
            nights = (booking.check_out - booking.check_in).days

            # Repair an old zero-amount Cash payment
            if (
                payment.payment_method == "Cash"
                and (payment.amount is None or payment.amount <= 0)
            ):

                if nights <= 0:
                    return HttpResponse(
                        "Cannot update payment: invalid booking dates.",
                        status=400,
                    )

                payment.amount = (
                    Decimal(str(booking.room.price)) * nights
                ).quantize(Decimal("0.01"))

            # Email only when status changes to Paid
            becoming_paid = (
                old_status != "Paid"
                and payment.status == "Paid"
            )

            # Do not allow a zero or negative amount to be marked Paid
            if becoming_paid:

                if payment.amount is None or payment.amount <= 0:
                    return HttpResponse(
                        "Cannot confirm payment: amount must be greater than zero.",
                        status=400,
                    )

                if payment.payment_method == "Cash" and nights <= 0:
                    return HttpResponse(
                        "Cannot confirm cash payment: invalid booking dates.",
                        status=400,
                    )

            payment.save()

            # Send receipt email only on the first transition to Paid
            if becoming_paid:

                try:
                    send_booking_email(
                        customer_email=booking.user.email,
                        customer_name=(
                            booking.user.get_full_name()
                            or booking.user.username
                        ),
                        booking_id=booking.id,
                        room=booking.room.room_number,
                        check_in=booking.check_in,
                        check_out=booking.check_out,
                        guests=booking.adults + booking.children,
                        amount=payment.amount,
                        payment_status=payment.status,
                        payment_method=payment.payment_method,
                    )

                except Exception as email_error:
                    print(
                        "Booking receipt email failed:",
                        str(email_error),
                    )

            return redirect("payment_list")

    else:
        form = PaymentForm(instance=payment)

    return render(
        request,
        "edit_payment.html",
        {"form": form},
    )



# 2 comment
# ==========================================
# Edit Payment
# ==========================================
# @login_required(login_url="login")
# @user_passes_test(lambda u: u.is_staff, login_url="home")
# def edit_payment(request, pk):

#     payment = get_object_or_404(
#         Payment,
#         pk=pk
#     )

#     if request.method == "POST":

#         # Purana status save kar lo
#         old_status = payment.status

#         form = PaymentForm(
#             request.POST,
#             instance=payment
#         )

#         if form.is_valid():

#             payment = form.save()

#             # Sirf Pending -> Paid hone par email bhejna
#             # if old_status != "Paid" and payment.status == "Paid":
#             if payment.status == "Paid":

#                 booking = payment.booking

#                 print("=" * 40)
#                 print("EMAIL FUNCTION CALLED")
#                 print("Customer Email:", booking.user.email)
#                 print("Customer Name:", booking.user.username)
#                 print("Payment Status:", payment.status)
#                 print("=" * 40)


#                 send_booking_email(

#                     customer_email=booking.user.email,

#                     customer_name=booking.user.get_full_name() or booking.user.username,

#                     booking_id=booking.id,

#                     room=booking.room.room_number,

#                     check_in=booking.check_in,

#                     check_out=booking.check_out,

#                     guests=booking.adults + booking.children,

#                     amount=payment.amount,

#                     payment_status=payment.status,

#                     payment_method=payment.payment_method,

#                 )

#             return redirect("payment_list")

#     else:

#         form = PaymentForm(
#             instance=payment
#         )

#     return render(
#         request,
#         "edit_payment.html",
#         {
#             "form": form
#         }
#     )


# 1 comment
# ==========================================
# Edit Payment
# ==========================================

# @login_required(login_url="login")
# def edit_payment(request, pk):

#     payment = get_object_or_404(Payment, pk=pk)

#     if request.method == "POST":

#         old_status = payment.status

#         print("=================================")
#         print("OLD STATUS :", old_status)

#         form = PaymentForm(
#             request.POST,
#             instance=payment
#         )

#         if form.is_valid():

#             payment = form.save()

#             print("NEW STATUS :", payment.status)

#             if old_status != "Paid" and payment.status == "Paid":

#                 print("EMAIL FUNCTION CALLED")

#                 booking = payment.booking

#                 send_booking_email(
#                     customer_email=booking.user.email,
#                     customer_name=booking.user.get_full_name() or booking.user.username,
#                     booking_id=booking.id,
#                     room=booking.room.room_number,
#                     check_in=booking.check_in,
#                     check_out=booking.check_out,
#                     guests=booking.adults + booking.children,
#                     amount=payment.amount,
#                     payment_status=payment.status,
#                 )

#             return redirect("payment_list")

#     else:
#         form = PaymentForm(instance=payment)

#     return render(
#         request,
#         "edit_payment.html",
#         {"form": form}
#     )



# ==========================================
# Delete Payment
# ==========================================
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_staff, login_url="home")
def delete_payment(request, pk):

    payment = get_object_or_404(
        Payment,
        pk=pk
    )

    payment.delete()

    return redirect("payment_list")


# ==========================================
# Payment Receipt Page
# ==========================================
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_staff, login_url="home")
def payment_receipt(request, pk):

    payment = get_object_or_404(
        Payment,
        pk=pk
    )

    return render(
        request,
        "payment_receipt.html",
        {
            "payment": payment
        }
    )

    # ======================================
# Export Payments to Excel
# ======================================

def export_payments_excel(request):

    workbook = Workbook()

    sheet = workbook.active

    sheet.title = "Payments"

    sheet.append([
        "Receipt No",
        "Customer",
        "Room",
        "Amount",
        "Method",
        "Status",
        "Payment Date"
    ])

    payments = Payment.objects.all()

    for payment in payments:

        sheet.append([

            payment.receipt_number,

            payment.booking.user.username,

            payment.booking.room.room_number,

            float(payment.amount),

            payment.payment_method,

            payment.status,

            str(payment.payment_date)

        ])

    response = HttpResponse(

        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    )

    response["Content-Disposition"] = (

        'attachment; filename="Payments.xlsx"'

    )

    workbook.save(response)

    return response


# ==========================================
# Payment Receipt PDF
# ==========================================
@login_required(login_url="login")
def payment_receipt_pdf(request, pk):

    payment = get_object_or_404(
        Payment,
        pk=pk
    )

    response = HttpResponse(
        content_type="application/pdf"
    )

    response["Content-Disposition"] = (
        f'attachment; filename="{payment.receipt_number}.pdf"'
    )

    doc = SimpleDocTemplate(response)

    styles = getSampleStyleSheet()

    elements = []

    elements.append(
        Paragraph(
            "<b>SMART HOTEL MANAGEMENT SYSTEM</b>",
            styles["Title"]
        )
    )

    elements.append(
        Paragraph("<br/>", styles["Normal"])
    )

    data = [

        ["Receipt Number", payment.receipt_number],

        ["Customer", payment.booking.user.username],

        ["Room", payment.booking.room.room_number],

        ["Check In", str(payment.booking.check_in)],

        ["Check Out", str(payment.booking.check_out)],

        ["Amount", f"₹ {payment.amount}"],

        ["Payment Method", payment.payment_method],

        ["Status", payment.status],

        ["Payment Date", str(payment.payment_date)],

    ]

    table = Table(
        data,
        colWidths=[180, 250]
    )

    table.setStyle(

        TableStyle([

            ("GRID", (0, 0), (-1, -1), 1, colors.black),

            ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),

            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),

            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),

        ])

    )

    elements.append(table)

    doc.build(elements)

    return response


# ======================================
# Export All Payments PDF
# ======================================

@login_required(login_url="login")
@user_passes_test(lambda u: u.is_staff, login_url="home")
def export_payments_pdf(request):

    response = HttpResponse(
        content_type="application/pdf"
    )

    response["Content-Disposition"] = (
        'attachment; filename="Payment_Report.pdf"'
    )

    document = SimpleDocTemplate(response)

    styles = getSampleStyleSheet()

    elements = []

    # Report Title
    elements.append(
        Paragraph(
            "<b>SMART HOTEL MANAGEMENT SYSTEM</b>",
            styles["Title"]
        )
    )

    elements.append(
        Paragraph(
            "Payment Report",
            styles["Heading2"]
        )
    )

    # Table Heading
    data = [[
        "Receipt",
        "Customer",
        "Room",
        "Amount",
        "Method",
        "Status"
    ]]

    # Database Data
    payments = Payment.objects.all()

    for payment in payments:

        data.append([

            payment.receipt_number,

            payment.booking.user.username,

            payment.booking.room.room_number,

            f"₹ {payment.amount}",

            payment.payment_method,

            payment.status

        ])

    table = Table(data)

    table.setStyle(

        TableStyle([

            ("BACKGROUND", (0,0), (-1,0), colors.grey),

            ("TEXTCOLOR", (0,0), (-1,0), colors.white),

            ("GRID", (0,0), (-1,-1), 1, colors.black),

            ("BACKGROUND", (0,1), (-1,-1), colors.beige),

            ("ALIGN", (0,0), (-1,-1), "CENTER"),

            ("BOTTOMPADDING", (0,0), (-1,0), 8),

        ])

    )

    elements.append(table)

    document.build(elements)

    return response



# ==========================================
# Razorpay Client
# ==========================================

def get_razorpay_client():
    if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
        raise ValueError("Razorpay API keys are not configured.")

    return razorpay.Client(
        auth=(
            settings.RAZORPAY_KEY_ID,
            settings.RAZORPAY_KEY_SECRET,
        )
    )


# ==========================================
# Create Razorpay Order
# ==========================================

@login_required(login_url="login")
def razorpay_create_order(request, booking_id):
    booking = get_object_or_404(
        Booking,
        pk=booking_id,
        user=request.user,
    )

    # if booking.status not in ["Pending", "Approved", "Confirmed"]:
    #     return HttpResponse(
    #         "Payment is not available for this booking status.",
    #         status=400,
    #     )

    if booking.status != "Approved":
        return HttpResponse(
            "Payment is available only after admin approval.",
            status=400
    )

    nights = (booking.check_out - booking.check_in).days

    if nights <= 0:
        return HttpResponse(
            "Invalid booking dates.",
            status=400,
        )

    # Amount is calculated on the server, not taken from the browser.
    total_amount = (
        Decimal(booking.room.price) * nights
    ).quantize(Decimal("0.01"))

    if total_amount <= 0:
        return HttpResponse(
            "Invalid payment amount.",
            status=400,
        )

    # Do not create another order if this booking is already paid.
    if booking.payments.filter(status="Paid").exists():
        return HttpResponse(
            "This booking already has a paid payment.",
            status=400,
        )

    try:
        client = get_razorpay_client()

        payment = Payment.objects.create(
            booking=booking,
            amount=total_amount,
            payment_method="Razorpay",
            status="Pending",
        )

        order = client.order.create(
            data={
                "amount": int(total_amount * 100),
                "currency": "INR",
                "receipt": payment.receipt_number,
            }
        )

        payment.razorpay_order_id = order["id"]
        payment.save(
            update_fields=["razorpay_order_id"]
        )

    except Exception:
        if "payment" in locals():
            payment.delete()

        return HttpResponse(
            "Could not create Razorpay order. Check your Test Mode keys and server logs.",
            status=502,
        )

    return render(
        request,
        "payments/razorpay_checkout.html",
        {
            "booking": booking,
            "payment": payment,
            "razorpay_key_id": settings.RAZORPAY_KEY_ID,
            "razorpay_order_id": order["id"],
            "amount_paise": int(total_amount * 100),
        },
    )


# ==========================================
# Verify Razorpay Payment
# ==========================================

# @login_required(login_url="login")
# @require_POST
# def razorpay_verify_payment(request):
#     try:
#         data = json.loads(request.body)

#         order_id = data.get("razorpay_order_id")
#         payment_id = data.get("razorpay_payment_id")
#         signature = data.get("razorpay_signature")

#         if not all([order_id, payment_id, signature]):
#             return JsonResponse(
#                 {"success": False, "message": "Missing payment details."},
#                 status=400,
#             )

#         # Find the order in our own database first.
#         payment = get_object_or_404(
#             Payment,
#             razorpay_order_id=order_id,
#             booking__user=request.user,
#         )

#         if payment.status == "Paid":
#             return JsonResponse({
#                 "success": True,
#                 "message": "Payment has already been verified.",
#                 "receipt_url": f"/payment/receipt/pdf/{payment.pk}/",
#             })

#         client = get_razorpay_client()

#         # Verify the signature using the stored server-side order ID.
#         client.utility.verify_payment_signature({
#             "razorpay_order_id": payment.razorpay_order_id,
#             "razorpay_payment_id": payment_id,
#             "razorpay_signature": signature,
#         })

#         # Fetch payment status directly from Razorpay.
#         remote_payment = client.payment.fetch(payment_id)

#         if remote_payment.get("order_id") != payment.razorpay_order_id:
#             return JsonResponse(
#                 {"success": False, "message": "Payment order mismatch."},
#                 status=400,
#             )

#         expected_amount = int(payment.amount * 100)

#         if remote_payment.get("amount") != expected_amount:
#             return JsonResponse(
#                 {"success": False, "message": "Payment amount mismatch."},
#                 status=400,
#             )

#         # Mark Paid only after Razorpay reports a captured payment.
#         if remote_payment.get("status") != "captured":
#             return JsonResponse(
#                 {
#                     "success": False,
#                     "message": (
#                         "Payment is not captured yet. "
#                         "Check Razorpay capture settings."
#                     ),
#                 },
#                 status=400,
#             )

#         payment.razorpay_payment_id = payment_id
#         payment.status = "Paid"
#         payment.save(
#             update_fields=[
#                 "razorpay_payment_id",
#                 "status",
#             ]
#         )

#         return JsonResponse({
#             "success": True,
#             "message": "Payment verified successfully.",
#             "receipt_url": f"/payment/receipt/pdf/{payment.pk}/",
#         })

#     except Payment.DoesNotExist:
#         return JsonResponse(
#             {"success": False, "message": "Payment record not found."},
#             status=404,
#         )
#     except Exception:
#         return JsonResponse(
#             {
#                 "success": False,
#                 "message": (
#                     "Payment verification failed. "
#                     "Check the server logs and Razorpay Dashboard."
#                 ),
#             },
#             status=400,
#         )




# ==========================================
# Verify Razorpay Payment
# ==========================================

@login_required(login_url="login")
@require_POST
def razorpay_verify_payment(request):
    try:
        data = json.loads(request.body)

        order_id = data.get("razorpay_order_id")
        payment_id = data.get("razorpay_payment_id")
        signature = data.get("razorpay_signature")

        if not all([order_id, payment_id, signature]):
            return JsonResponse(
                {
                    "success": False,
                    "message": "Missing payment details."
                },
                status=400,
            )

        # Find the payment belonging to the logged-in customer.
        payment = get_object_or_404(
            Payment,
            razorpay_order_id=order_id,
            booking__user=request.user,
        )

        # Prevent a second payment ID from overwriting a verified payment.
        if payment.status == "Paid":
            if payment.razorpay_payment_id == payment_id:
                return JsonResponse({
                    "success": True,
                    "message": "Payment verified successfully.",
                    "receipt_url": reverse("customer_dashboard"),
                    # "receipt_url": f"/payment/receipt/pdf/{payment.pk}/",
                    # "message": "Payment has already been verified.",

                })

            return JsonResponse(
                {
                    "success": False,
                    "message": "This order is already marked as paid."
                },
                status=409,
            )

        client = get_razorpay_client()

        # Verify Razorpay's signature.
        client.utility.verify_payment_signature({
            "razorpay_order_id": payment.razorpay_order_id,
            "razorpay_payment_id": payment_id,
            "razorpay_signature": signature,
        })

        # Fetch payment details directly from Razorpay.
        remote_payment = client.payment.fetch(payment_id)

        # Verify order, amount and currency.
        if remote_payment.get("order_id") != payment.razorpay_order_id:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Payment order mismatch."
                },
                status=400,
            )

        expected_amount = int(payment.amount * 100)

        if remote_payment.get("amount") != expected_amount:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Payment amount mismatch."
                },
                status=400,
            )

        if remote_payment.get("currency") != "INR":
            return JsonResponse(
                {
                    "success": False,
                    "message": "Payment currency mismatch."
                },
                status=400,
            )

        # Mark as Paid only after Razorpay confirms capture.
        if remote_payment.get("status") != "captured":
            return JsonResponse(
                {
                    "success": False,
                    "message": (
                        "Payment is not captured yet. "
                        "Check Razorpay capture settings."
                    ),
                },
                status=400,
            )

        # Save verified transaction details.
        payment.razorpay_payment_id = payment_id
        payment.status = "Paid"
        payment.payment_method = "Razorpay"

        payment.save(
            update_fields=[
                "razorpay_payment_id",
                "status",
                "payment_method",
            ]
        )

        # Send the existing booking confirmation email.
        # Email failure must not undo a verified payment.
        booking = payment.booking

        try:
            send_booking_email(
                customer_email=booking.user.email,
                customer_name=(
                    booking.user.get_full_name()
                    or booking.user.username
                ),
                booking_id=booking.id,
                room=booking.room.room_number,
                check_in=booking.check_in,
                check_out=booking.check_out,
                guests=booking.adults + booking.children,
                amount=payment.amount,
                payment_status=payment.status,
                payment_method=payment.payment_method,
            )
        except Exception as email_error:
            print(
                "Booking email failed after payment verification:",
                str(email_error)
            )

        return JsonResponse({
            "success": True,
            "message": "Payment verified successfully.",
            "receipt_url": f"/payment/receipt/pdf/{payment.pk}/",
        })

    except json.JSONDecodeError:
        return JsonResponse(
            {
                "success": False,
                "message": "Invalid JSON request."
            },
            status=400,
        )

    except razorpay.errors.SignatureVerificationError:
        return JsonResponse(
            {
                "success": False,
                "message": "Invalid Razorpay payment signature."
            },
            status=400,
        )

    except Exception as error:
        print("Razorpay verification error:", str(error))

        return JsonResponse(
            {
                "success": False,
                "message": (
                    "Payment verification failed. "
                    "Check the server terminal for details."
                ),
            },
            status=400,
        )


# =========================
# CUSTOMER REFUND VIEWS
# =========================

@login_required
def request_refund(request, payment_id):
    payment = get_object_or_404(
        Payment,
        pk=payment_id,
        booking__user=request.user
    )

    # Only successfully paid payments can be refunded.
    if payment.status != "Paid":
        messages.error(
            request,
            "Refund request sirf successful payment ke liye ki ja sakti hai."
        )
        return redirect("my_payments")

    # Do not allow another request for the same payment.
    if RefundRequest.objects.filter(payment=payment).exists():
        messages.info(
            request,
            "Is payment ke liye refund request pehle se maujood hai."
        )
        return redirect("my_refund_requests")

    if request.method == "POST":
        reason = request.POST.get("reason", "").strip()

        if not reason:
            messages.error(request, "Refund ka reason enter karo.")
        elif len(reason) > 2000:
            messages.error(
                request,
                "Refund reason 2000 characters se kam hona chahiye."
            )
        else:
            RefundRequest.objects.create(
                payment=payment,
                reason=reason,
                amount=payment.amount,
                status="Requested"
            )

            messages.success(
                request,
                "Aapki refund request successfully submit ho gayi."
            )
            return redirect("my_refund_requests")

    return render(
        request,
        "payments/request_refund.html",
        {"payment": payment}
    )


@login_required
def my_refund_requests(request):
    refund_requests = RefundRequest.objects.filter(
        payment__booking__user=request.user
    ).select_related("payment", "payment__booking")

    return render(
        request,
        "payments/my_refund_requests.html",
        {"refund_requests": refund_requests}
    )


# =========================
# ADMIN REFUND VIEWS
# =========================

@login_required
@user_passes_test(lambda user: user.is_staff)
def admin_refund_list(request):
    refund_requests = RefundRequest.objects.select_related(
        "payment",
        "payment__booking"
    ).all()

    return render(
        request,
        "payments/admin_refund_list.html",
        {"refund_requests": refund_requests}
    )


@login_required
@user_passes_test(lambda user: user.is_staff)
def process_refund(request, refund_id):
    if request.method != "POST":
        return redirect("admin_refund_list")

    refund = get_object_or_404(
        RefundRequest.objects.select_related("payment"),
        pk=refund_id
    )

    if refund.status not in ["Requested", "Approved"]:
        messages.warning(
            request,
            "Ye refund request already process ho chuki hai."
        )
        return redirect("admin_refund_list")

    action = request.POST.get("action")
    admin_note = request.POST.get("admin_note", "").strip()
    payment = refund.payment

    # Admin rejects the request.
    if action == "reject":
        refund.status = "Rejected"
        refund.admin_note = admin_note or "Refund request rejected by admin."
        refund.save(update_fields=[
            "status", "admin_note", "updated_at"
        ])

        messages.success(request, "Refund request reject kar di gayi.")
        return redirect("admin_refund_list")

    # Razorpay refunds must be processed through Razorpay.
    if action == "approve" and payment.payment_method == "Razorpay":
        if not payment.razorpay_payment_id:
            messages.error(
                request,
                "Razorpay payment ID nahi mili. Refund process nahi hua."
            )
            return redirect("admin_refund_list")

        try:
            client = get_razorpay_client()

            # Razorpay amount is sent in paise, not rupees.
            amount_in_paise = int(refund.amount * 100)

            result = client.payment.refund(
                payment.razorpay_payment_id,
                {
                    "amount": amount_in_paise,
                    "notes": {
                        "reason": refund.reason[:200]
                    }
                }
            )

            refund.razorpay_refund_id = result.get("id")
            razorpay_status = result.get("status", "").lower()
            refund.admin_note = admin_note

            if razorpay_status == "processed":
                refund.status = "Processed"
                refund.processed_at = timezone.now()
                payment.status = "Refunded"
                payment.save(update_fields=["status"])

                messages.success(
                    request,
                    "Razorpay ne refund processed report kiya hai."
                )

            elif razorpay_status == "failed":
                refund.status = "Failed"
                messages.error(
                    request,
                    "Razorpay refund fail report kar raha hai. Payment Paid hi rahega."
                )

            else:
                # For example, Razorpay may report a pending refund.
                refund.status = "Processing"
                messages.info(
                    request,
                    "Refund request Razorpay ko bhej di gayi hai. Final status verify karna hoga."
                )

            refund.save()

        except Exception:
            # Don't mark the payment as refunded if the API call fails.
            refund.status = "Failed"
            refund.admin_note = (
                (admin_note + "\n" if admin_note else "")
                + "Razorpay API call failed. Check server logs and Razorpay Dashboard."
            )
            refund.save(update_fields=[
                "status", "admin_note", "updated_at"
            ])

            messages.error(
                request,
                "Razorpay refund process nahi hua. Razorpay Dashboard aur server logs check karo."
            )

        return redirect("admin_refund_list")

    # For cash, UPI, card payments handled outside Razorpay,
    # an admin must explicitly record the manual refund.
    if action == "manual_complete":
        if payment.payment_method == "Razorpay":
            messages.error(
                request,
                "Razorpay payment ke liye manual completion use nahi kar sakte."
            )
            return redirect("admin_refund_list")

        if not admin_note:
            messages.error(
                request,
                "Manual refund complete karne ke liye admin note zaroori hai."
            )
            return redirect("admin_refund_list")

        refund.status = "Processed"
        refund.admin_note = admin_note
        refund.processed_at = timezone.now()
        refund.save()

        payment.status = "Refunded"
        payment.save(update_fields=["status"])

        messages.success(
            request,
            "Manual refund record ho gaya. Ensure karo ki amount customer ko actually return ho chuka ho."
        )
        return redirect("admin_refund_list")

    messages.error(request, "Invalid refund action.")
    return redirect("admin_refund_list")