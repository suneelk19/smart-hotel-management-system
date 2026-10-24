from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from datetime import date

from .models import Room
from .forms import RoomForm


# --------------------------
# Room List + Search + Date-wise Availability
# --------------------------
def room_list(request):

    query = request.GET.get("q", "")
    check_in_str = request.GET.get("check_in", "")
    check_out_str = request.GET.get("check_out", "")

    rooms = Room.objects.all()

    # Customer: show only rooms marked available
    if not request.user.is_staff:
        rooms = rooms.filter(available=True)

    if query:
        rooms = rooms.filter(
            Q(room_number__icontains=query) |
            Q(room_type__icontains=query)
        )

    # -----------------------------------------------
    # Date-wise availability filter (non-staff only)
    # When check_in and check_out are provided,
    # exclude rooms with conflicting bookings.
    # -----------------------------------------------
    check_in = None
    check_out = None
    date_filter_active = False
    date_error = ""

    if not request.user.is_staff and check_in_str and check_out_str:
        try:
            check_in = date.fromisoformat(check_in_str)
            check_out = date.fromisoformat(check_out_str)

            if check_out <= check_in:
                date_error = "Check-out date must be after check-in date."
            elif check_in < date.today():
                date_error = "Check-in date cannot be in the past."
            else:
                # Find room IDs with conflicting bookings
                from booking.models import Booking
                conflicting_room_ids = Booking.objects.filter(
                    status__in=["Pending", "Approved", "Confirmed"],
                    check_in__lt=check_out,
                    check_out__gt=check_in,
                ).values_list("room_id", flat=True)

                rooms = rooms.exclude(id__in=conflicting_room_ids)
                date_filter_active = True

        except (ValueError, TypeError):
            date_error = "Invalid date format. Please use the date picker."

    return render(
        request,
        "room_list.html",
        {
            "rooms": rooms,
            "query": query,
            "check_in": check_in_str,
            "check_out": check_out_str,
            "date_filter_active": date_filter_active,
            "date_error": date_error,
        }
    )



# --------------------------
# Public Room Details
# --------------------------
def room_detail(request, pk):
    room = get_object_or_404(Room, pk=pk)

    # Customers ko unavailable rooms ki details bhi
    # dekhne dein; booking availability alag check hogi.
    if not request.user.is_staff and not room.available:
        # Details public hain, isliye room ko hide nahi karna.
        pass

    return render(
        request,
        "room_detail.html",
        {
            "room": room,
        }
    )



# --------------------------
# Add Room
# --------------------------
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_staff, login_url="home")
def add_room(request):

    if request.method == "POST":

        form = RoomForm(request.POST, request.FILES)

        if form.is_valid():

            form.save()

            return redirect("rooms")

        else:

            print(form.errors)

    else:

        form = RoomForm()

    return render(
        request,
        "add_room.html",
        {
            "form": form
        }
    )


# --------------------------
# Edit Room
# --------------------------
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_staff, login_url="home")
def edit_room(request, pk):

    room = get_object_or_404(Room, pk=pk)

    if request.method == "POST":

        form = RoomForm(
            request.POST,
            request.FILES,
            instance=room
        )

        if form.is_valid():

            form.save()

            return redirect("rooms")

    else:

        form = RoomForm(instance=room)

    return render(
        request,
        "edit_room.html",
        {
            "form": form
        }
    )


# --------------------------
# Delete Room
# --------------------------
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_staff, login_url="home")
def delete_room(request, pk):

    room = get_object_or_404(Room, pk=pk)

    room.delete()

    return redirect("rooms")