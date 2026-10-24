from django.urls import path
from . import views

urlpatterns = [

    path(
        "",
        views.room_list,
        name="rooms"
    ),

    path(
        "add/",
        views.add_room,
        name="add_room"
    ),

    path(
        "edit/<int:pk>/",
        views.edit_room,
        name="edit_room"
    ),

    path(
        "delete/<int:pk>/",
        views.delete_room,
        name="delete_room"
    ),

    path(
        "detail/<int:pk>/",
        views.room_detail,
        name="room_detail"
    ),

]