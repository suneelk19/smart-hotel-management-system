from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Staff
from .forms import StaffForm
from django.db.models import Q


# -----------------------------
# Staff List
# -----------------------------
# def staff_list(request):

#     staffs = Staff.objects.all()

#     return render(
#         request,
#         "staff_list.html",
#         {
#             "staffs": staffs
#         }
#     )

@login_required(login_url="login")
@user_passes_test(lambda u: u.is_staff, login_url="home")
def staff_list(request):

    query = request.GET.get("q", "")

    staffs = Staff.objects.all()

    if query:

        staffs = staffs.filter(

            Q(name__icontains=query) |

            Q(designation__icontains=query) |

            Q(phone__icontains=query) |

            Q(email__icontains=query)

        )

    return render(

        request,

        "staff_list.html",

        {

            "staffs": staffs,

            "query": query

        }

    )

# -----------------------------
# Add Staff
# -----------------------------
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_staff, login_url="home")
def add_staff(request):

    if request.method == "POST":

        form = StaffForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect("staff_list")

    else:

        form = StaffForm()

    return render(
        request,
        "add_staff.html",
        {
            "form": form
        }
    )


# -----------------------------
# Edit Staff
# -----------------------------
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_staff, login_url="home")
def edit_staff(request, pk):

    staff = get_object_or_404(
        Staff,
        pk=pk
    )

    if request.method == "POST":

        form = StaffForm(
            request.POST,
            instance=staff
        )

        if form.is_valid():

            form.save()

            return redirect("staff_list")

    else:

        form = StaffForm(
            instance=staff
        )

    return render(
        request,
        "edit_staff.html",
        {
            "form": form
        }
    )


# -----------------------------
# Delete Staff
# -----------------------------
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_staff, login_url="home")
def delete_staff(request, pk):

    staff = get_object_or_404(
        Staff,
        pk=pk
    )

    staff.delete()

    return redirect("staff_list")