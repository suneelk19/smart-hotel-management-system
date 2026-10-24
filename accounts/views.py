from django.core.mail import send_mail
from django.conf import settings

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test

from .forms import RegisterForm

# Models
from rooms.models import Room
from booking.models import Booking
from payments.models import Payment
from feedback.models import Feedback
from staff.models import Staff
from customer.models import CustomerProfile
from django.db.models import Sum, Q
from django.utils.timezone import now


# =====================================
# Home Page
# =====================================
def home(request):
    return render(request, "index.html")


# =====================================
# Register
# =====================================
def register(request):

    if request.method == "POST":

        form = RegisterForm(request.POST)

        if form.is_valid():

            User.objects.create_user(
                first_name=form.cleaned_data["first_name"],
                last_name=form.cleaned_data["last_name"],
                username=form.cleaned_data["username"],
                email=form.cleaned_data["email"],
                password=form.cleaned_data["password"],
            )

            messages.success(request, "Registration Successful!")
            return redirect("login")

    else:
        form = RegisterForm()

    return render(request, "register.html", {"form": form})



# =====================================
# Login
# =====================================
def user_login(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is not None:

            login(request, user)

            messages.success(
                request,
                f"Welcome {user.username}!"
            )

            # ===============================
            # Admin Login
            # ===============================
            if user.is_staff:
                return redirect("admin_dashboard")

            # ===============================
            # Customer Login
            # ===============================
            else:
                return redirect("customer_dashboard")

        else:

            messages.error(
                request,
                "Invalid Username or Password"
            )

    return render(
        request,
        "login.html"
    )


# =====================================
# Logout
# =====================================
def user_logout(request):

    logout(request)

    messages.success(request, "Logout Successful!")

    return redirect("home")


# =====================================
# User Dashboard
# =====================================
@login_required(login_url="login")
@user_passes_test(lambda u: not u.is_staff, login_url="home")
def dashboard(request):

    my_bookings = Booking.objects.filter(user=request.user)

    context = {

        "my_bookings": my_bookings.count(),

        "pending_bookings": my_bookings.filter(
            status="Pending"
        ).count(),

        "approved_bookings": my_bookings.filter(
            status="Approved"
        ).count(),

        "rejected_bookings": my_bookings.filter(
            status="Rejected"
        ).count(),

        "payments": Payment.objects.filter(
            booking__user=request.user
        ).count(),

        "feedbacks": Feedback.objects.filter(
            user=request.user
        ).count(),
    }

    return render(
        request,
        "dashboard.html",
        context,
    )


# ==========================
# Admin Dashboard
# ==========================
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_staff, login_url="home")
def admin_dashboard(request):

    context = {

        # ======================
        # Dashboard Cards
        # ======================

        "total_rooms": Room.objects.count(),

        "available_rooms": Room.objects.filter(
            available=True
        ).count(),

        "occupied_rooms": Room.objects.filter(
            available=False
        ).count(),

        "total_bookings": Booking.objects.count(),

        "total_customers": User.objects.filter(
            is_staff=False
        ).count(),

        "total_staff": Staff.objects.count(),

        "total_feedback": Feedback.objects.count(),

        "total_payments": Payment.objects.count(),

        # ======================
        # Booking Status Count
        # ======================

        "pending": Booking.objects.filter(
            status="Pending"
        ).count(),

        "approved": Booking.objects.filter(
            status="Approved"
        ).count(),

        "confirmed": Booking.objects.filter(
            status="Confirmed"
        ).count(),

        "rejected": Booking.objects.filter(
            status="Rejected"
        ).count(),

        "cancelled": Booking.objects.filter(
            status="Cancelled"
        ).count(),


                # ======================
        # Dashboard Statistics
        # Add BELOW "cancelled"
        # ======================

        "total_revenue": Payment.objects.filter(
            status="Paid"
        ).aggregate(
            Sum("amount")
        )["amount__sum"] or 0,

        "today_bookings": Booking.objects.filter(
            check_in=now().date()
        ).count(),



        # ======================
# Recent Records
# ======================

    "recent_bookings": Booking.objects.select_related(
    "user",
    "room"
    ).order_by("-booking_date")[:5],

"recent_payments": Payment.objects.select_related(
    "booking",
    "booking__user"
).order_by("-payment_date")[:5],

"recent_staff": Staff.objects.order_by(
    "-joining_date"
)[:5],

"recent_feedback": Feedback.objects.select_related(
    "user"
).order_by("-created_at")[:5],



    }




    return render(
        request,
        "admin_dashboard.html",
        context,
    )



    # =====================================
# Test Email
# =====================================

from django.http import HttpResponse


def test_email(request):

    send_mail(
        subject="Smart Hotel Email Test",
        message="""
Hello,

Congratulations!

Your Smart Hotel Email Configuration is working successfully.

This is a test email sent from your Django Project.

Thank You
Smart Hotel Team
""",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[settings.EMAIL_HOST_USER],
        fail_silently=False,
    )

    return HttpResponse("✅ Test Email Sent Successfully.")


# =====================================
# Admin: Customer List
# =====================================

@login_required(login_url="login")
@user_passes_test(lambda u: u.is_staff, login_url="home")
def customer_list(request):

    query = request.GET.get("q", "")

    customers = User.objects.filter(is_staff=False)

    if query:
        customers = customers.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )

    # Ensure every customer has a CustomerProfile (create only, never update)
    for customer in customers:
        CustomerProfile.objects.get_or_create(
            user=customer,
            defaults={
                "phone": "",
                "address": "",
                "city": "",
                "state": "",
                "country": "India",
                "pincode": "",
            }
        )

    return render(
        request,
        "customer_list_admin.html",
        {
            "customers": customers,
            "query": query,
        }
    )


# =====================================
# Admin: Customer Detail
# =====================================

@login_required(login_url="login")
@user_passes_test(lambda u: u.is_staff, login_url="home")
def customer_detail_admin(request, pk):

    customer = get_object_or_404(User, pk=pk, is_staff=False)

    # Ensure profile exists (create only if missing, never update)
    profile, _ = CustomerProfile.objects.get_or_create(
        user=customer,
        defaults={
            "phone": "",
            "address": "",
            "city": "",
            "state": "",
            "country": "India",
            "pincode": "",
        }
    )

    # Only this customer's bookings
    bookings = Booking.objects.filter(user=customer).select_related("room")

    # Only this customer's payments
    payments = Payment.objects.filter(
        booking__user=customer
    ).select_related("booking", "booking__room")

    total_paid = payments.filter(status="Paid").aggregate(
        Sum("amount")
    )["amount__sum"] or 0

    return render(
        request,
        "customer_detail_admin.html",
        {
            "customer": customer,
            "profile": profile,
            "bookings": bookings,
            "payments": payments,
            "total_paid": total_paid,
        }
    )
