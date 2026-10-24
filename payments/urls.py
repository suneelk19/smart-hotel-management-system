
from django.urls import path
from . import views

urlpatterns = [

    path(
        "",
        views.payment_list,
        name="payment_list"
    ),

    path(
        "add/",
        views.add_payment,
        name="add_payment"
    ),

    path(
        "edit/<int:pk>/",
        views.edit_payment,
        name="edit_payment"
    ),

    path(
        "delete/<int:pk>/",
        views.delete_payment,
        name="delete_payment"
    ),

    path(
    "receipt/<int:pk>/",
    views.payment_receipt,
    name="payment_receipt"
    ),

    # PDF Receipt
    path(
        "receipt/pdf/<int:pk>/",
        views.payment_receipt_pdf,
        name="payment_receipt_pdf"
    ),


    # Export Excel
    path(
        "export/",
        views.export_payments_excel,
        name="export_payments_excel"
    ),

    # Export PDF
    path(
        "export/pdf/",
        views.export_payments_pdf,
        name="export_payments_pdf"
    ),

    path(
    "razorpay/create/<int:booking_id>/",
    views.razorpay_create_order,
    name="razorpay_create_order",
),

path(
    "razorpay/verify/",
    views.razorpay_verify_payment,
    name="razorpay_verify_payment",
),


# ==========================================
# Refund Management Routes
# ==========================================

path(
    "refund/request/<int:payment_id>/",
    views.request_refund,
    name="request_refund"
),

path(
    "refund/my-requests/",
    views.my_refund_requests,
    name="my_refund_requests"
),

path(
    "refund/admin/",
    views.admin_refund_list,
    name="admin_refund_list"
),

path(
    "refund/admin/<int:refund_id>/process/",
    views.process_refund,
    name="process_refund"
),
]