from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .ai_service import ask_ai_concierge



@login_required(login_url="login")
def ai_concierge(request):

    answer = None

    if request.method == "POST":

        user_message = request.POST.get(
            "message",
            ""
        ).strip()

        if user_message:

            answer = ask_ai_concierge(
                user_message,
                request.user
            )

    return render(
        request,
        "ai_concierge/chat.html",
        {
            "answer": answer,
        }
    )