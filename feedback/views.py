
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test

from .models import Feedback
from .forms import FeedbackForm
from django.db.models import Q




@login_required(login_url="login")
@user_passes_test(lambda u: u.is_staff, login_url="home")
def feedback_list(request):

    query = request.GET.get("q", "")

    feedbacks = Feedback.objects.all()

    if query:

        feedbacks = feedbacks.filter(

            Q(user__username__icontains=query) |

            Q(subject__icontains=query) |

            Q(rating__icontains=query)

        )

    return render(

        request,

        "feedback_list.html",

        {

            "feedbacks": feedbacks,

            "query": query

        }

    )


@login_required(login_url="login")
def add_feedback(request):

    if request.method == "POST":

        form = FeedbackForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect("feedback_list")

    else:

        form = FeedbackForm()

    return render(
        request,
        "add_feedback.html",
        {
            "form": form
        }
    )


@login_required(login_url="login")
def edit_feedback(request, pk):

    feedback = get_object_or_404(
        Feedback,
        pk=pk
    )

    if request.method == "POST":

        form = FeedbackForm(
            request.POST,
            instance=feedback
        )

        if form.is_valid():

            form.save()

            return redirect("feedback_list")

    else:

        form = FeedbackForm(
            instance=feedback
        )

    return render(
        request,
        "edit_feedback.html",
        {
            "form": form
        }
    )


@login_required(login_url="login")
@user_passes_test(lambda u: u.is_staff, login_url="home")
def delete_feedback(request, pk):

    feedback = get_object_or_404(
        Feedback,
        pk=pk
    )

    feedback.delete()

    return redirect("feedback_list")