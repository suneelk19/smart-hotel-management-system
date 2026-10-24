from django.urls import path

from . import views


urlpatterns = [

    path(
        "",
        views.ai_concierge,
        name="ai_concierge"
    ),

]