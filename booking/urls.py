from django.urls import path
from . import views

urlpatterns = [

    path(
        "",
        views.booking_list,
        name="booking_list"
    ),

    path(
        "add/",
        views.add_booking,
        name="add_booking"
    ),

    path(
        "edit/<int:pk>/",
        views.edit_booking,
        name="edit_booking"
    ),

    path(
        "delete/<int:pk>/",
        views.delete_booking,
        name="delete_booking"
    ),

    path(
        "approve/<int:pk>/",
        views.approve_booking,
        name="approve_booking"
    ),

    path(
        "reject/<int:pk>/",
        views.reject_booking,
        name="reject_booking"
    ),


    path(
    "export/",
    views.export_booking_csv,
    name="export_booking_csv"
),

]