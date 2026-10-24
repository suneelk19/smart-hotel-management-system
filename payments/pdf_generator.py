from io import BytesIO
import os

from django.conf import settings

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor


import qrcode
import tempfile

def generate_receipt(
    booking_id,
    customer_name,
    room,
    check_in,
    check_out,
    guests,
    amount,
    payment_status,
    payment_method="Cash",
):

    buffer = BytesIO()

    pdf = canvas.Canvas(buffer, pagesize=A4)

    pdf.setTitle("Smart Hotel Receipt")

    width, height = A4

    # =====================================
    # Hotel Logo
    # =====================================

    logo_path = os.path.join(
        settings.BASE_DIR,
        "static",
        "images",
        "hotel_logo.png"
    )

    print("BASE_DIR :", settings.BASE_DIR)
    print("LOGO PATH :", logo_path)
    print("EXISTS :", os.path.exists(logo_path))

    if os.path.exists(logo_path):

        print("Trying to load logo...")

        pdf.drawImage(
            logo_path,
            40,
            height - 90,
            width=60,
            height=60,
            preserveAspectRatio=True,
            mask="auto"
        )

    # =====================================
    # Hotel Header
    # =====================================

# =====================================
# HOTEL HEADER (Professional)
# =====================================

    pdf.setFillColor(HexColor("#1565C0"))
    pdf.setFont("Helvetica-Bold", 22)
    pdf.drawString(120, height - 45, "SMART HOTEL")

    pdf.setFillColor(HexColor("#000000"))
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(120, height - 65, "Luxury Hotel & Resort")

    pdf.setFont("Helvetica", 10)

    pdf.drawString(
    120,
    height - 82,
    "Near SG Highway, Satellite, Ahmedabad, Gujarat - 380015"
    )

    pdf.drawString(
    120,
    height - 97,
    "Phone : +91 9876543210"
    )

    pdf.drawString(
    120,
    height - 112,
    "Email : support@smarthotel.com"
    )

    pdf.drawString(
    120,
    height - 127,
    "Website : www.smarthotel.com"
    )

    pdf.drawString(
    120,
    height - 142,
    "GSTIN : 24ABCDE1234F1Z5"
    )

    # =====================================
    # Existing Booking Details
    # (Abhi same rakhe hain)
    # =====================================

# =====================================
# Invoice Header
# =====================================

    pdf.setFillColor(HexColor("#198754"))

    pdf.setFont("Helvetica-Bold", 18)

    pdf.drawString(
        40,
        680,
        "BOOKING RECEIPT"
    )

    pdf.setFillColor(HexColor("#000000"))

    pdf.setFont("Helvetica", 11)

    pdf.drawString(
        380,
        680,
        f"Invoice : INV-{booking_id:04d}"
    )

    pdf.drawString(
        380,
        660,
        f"Receipt : REC-{booking_id:04d}"
    )

    pdf.drawString(
        380,
        640,
        f"Booking ID : {booking_id}"
    )

# =====================================
# Customer Information Box
# =====================================

    pdf.roundRect(
    40,
    460,
    520,
    150,
    10
)

    pdf.setFont(
        "Helvetica-Bold",
        13
    )

    pdf.drawString(
        55,
        590,
        "Customer Details"
    )

    pdf.setFont(
        "Helvetica",
        11
    )

    pdf.drawString(
        60,
        565,
        f"Customer Name : {customer_name}"
    )

    pdf.drawString(
        60,
        540,
        f"Room Number : {room}"
    )

    pdf.drawString(
        60,
        515,
        f"Guests : {guests}"
    )

    pdf.drawString(
        60,
        490,
        f"Payment Status : {payment_status}"
    )

    pdf.drawString(
        60,
        465,
        f"Payment Method : {payment_method}"
    )

# =====================================
# Booking Information Box
# =====================================

    pdf.roundRect(
        40,
        290,
        520,
        140,
        10
    )

    pdf.setFont(
        "Helvetica-Bold",
        13
    )

    pdf.drawString(
        55,
        410,
        "Booking Details"
    )

    pdf.setFont(
        "Helvetica",
        11
    )

    pdf.drawString(
        60,
        385,
        f"Check In : {check_in}"
    )

    pdf.drawString(
        60,
        360,
        f"Check Out : {check_out}"
    )

    pdf.drawString(
        60,
        335,
        f"Booking Amount : ₹ {amount}"
    )


    # =====================================
    # Payment Summary
    # =====================================

    pdf.setFillColor(HexColor("#0d6efd"))
    pdf.setFont("Helvetica-Bold", 14)

    pdf.drawString(
        40,
        250,
        "Payment Summary"
    )

    pdf.setFillColor(HexColor("#000000"))
    pdf.setFont("Helvetica", 11)

    pdf.drawString(
        60,
        220,
        f"Base Room Charges: INR {float(amount) / 1.18:.2f}"
    )

    pdf.drawString(
        60,
        200,
        f"GST (18%): INR {float(amount) - (float(amount) / 1.18):.2f}"
    )

    pdf.drawString(
        60,
        180,
        "Other Charges: INR 0.00"
    )

    pdf.setFont("Helvetica-Bold", 12)

    pdf.drawString(
        60,
        150,
        f"TOTAL PAID: INR {float(amount):.2f}"
    )

# =====================================
# Payment Summary
# =====================================


    # pdf.drawString(
    #     40,
    #     250,
    #     "Payment Summary"
    # )

    # pdf.setFillColor(HexColor("#000000"))

    # pdf.setFont("Helvetica", 11)

    # pdf.drawString(
    #     60,
    #     220,
    #     f"Base Room Charges : ₹ {float(amount) / 1.18:.2f}"
    # )

    # pdf.drawString(
    #     60,
    #     200,
    #     f"GST (18%) : ₹ {float(amount) - (float(amount) / 1.18):.2f}"
    # )

    # pdf.drawString(
    #     60,
    #     180,
    #     "Other Charges : ₹ 0.00"
    # )

    # pdf.setFont(
    #     "Helvetica-Bold",
    #     12
    # )

    # pdf.drawString(
    #     60,
    #     150,
    #     f"TOTAL PAID : ₹ {amount}"
    # )

# =====================================
# Signature
# =====================================

    pdf.line(
        360,
        120,
        520,
        120
    )

    pdf.setFont(
        "Helvetica",
        10
    )

    pdf.drawString(
        385,
        105,
        "Authorized Signature"
    )

# =====================================
# Thank You
# =====================================

    pdf.setFont(
        "Helvetica-Bold",
        14
    )

    pdf.setFillColor(HexColor("#198754"))

    pdf.drawCentredString(
        300,
        70,
        "Thank You For Choosing Smart Hotel!"
    )

    pdf.setFont(
        "Helvetica",
        10
    )

    pdf.setFillColor(HexColor("#000000"))

    pdf.drawCentredString(
        300,
        50,
        "We hope to see you again soon."
    )

# =====================================
# Footer
# =====================================

    pdf.setStrokeColor(HexColor("#0d6efd"))

    pdf.line(
        40,
        35,
        560,
        35
    )

    pdf.setFont(
        "Helvetica",
        9
    )

    pdf.drawCentredString(
        300,
        20,
        "Generated Automatically by Smart Hotel Management System"
    )



# =====================================
# Generate QR Code
# =====================================

#     qr_data = f"""
#     Booking ID : {booking_id}
#     Customer : {customer_name}
#     Room : {room}
#     Status : {payment_status}
#     Method : {payment_method}
#     Amount : ₹ {amount}
#     """

#     qr = qrcode.make(qr_data)

#     temp_file = tempfile.NamedTemporaryFile(
#     suffix=".png",
#     delete=False
#     )

#     qr.save(temp_file.name)

# # Draw QR Code in PDF
#     pdf.drawImage(
#         temp_file.name,
#         430,
#         170,
#         width=100,
#         height=100
#     )

#     pdf.setFont("Helvetica", 9)

#     pdf.drawString(
#         430,
#         155,
#         "Scan to Verify Booking"
#     )

#     pdf.save()

#     pdf_data = buffer.getvalue()

#     buffer.close()


#     return pdf_data


    # =====================================
    # Generate QR Code
    # =====================================

    qr_data = f"""
Booking ID: {booking_id}
Customer: {customer_name}
Room: {room}
Check In: {check_in}
Check Out: {check_out}
Payment Status: {payment_status}
Payment Method: {payment_method}
Amount: INR {float(amount):.2f}
"""

    qr = qrcode.make(qr_data)

    temp_file = tempfile.NamedTemporaryFile(
        suffix=".png",
        delete=False
    )

    try:
        temp_file.close()
        qr.save(temp_file.name)

        # Draw QR Code in PDF
        pdf.drawImage(
            temp_file.name,
            430,
            170,
            width=100,
            height=100,
            preserveAspectRatio=True,
            mask="auto"
        )

        pdf.setFont("Helvetica", 9)

        pdf.drawString(
            430,
            155,
            "Scan to Verify Booking"
        )

    finally:
        # Remove temporary QR image
        if os.path.exists(temp_file.name):
            os.remove(temp_file.name)

    # =====================================
    # Save PDF
    # =====================================

    pdf.save()

    pdf_data = buffer.getvalue()
    buffer.close()

    return pdf_data