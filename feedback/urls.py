

from django.urls import path
from . import views

urlpatterns = [

    path(
        "",
        views.feedback_list,
        name="feedback_list"
    ),

    path(
        "add/",
        views.add_feedback,
        name="add_feedback"
    ),

    path(
        "edit/<int:pk>/",
        views.edit_feedback,
        name="edit_feedback"
    ),

    path(
        "delete/<int:pk>/",
        views.delete_feedback,
        name="delete_feedback"
    ),



]