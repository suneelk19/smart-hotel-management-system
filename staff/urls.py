from django.urls import path
from . import views

urlpatterns = [

    path("", views.staff_list, name="staff_list"),

    path("add/", views.add_staff, name="add_staff"),

    path("edit/<int:pk>/", views.edit_staff, name="edit_staff"),

    path("delete/<int:pk>/", views.delete_staff, name="delete_staff"),

]