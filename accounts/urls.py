from django.urls import path
from . import views

urlpatterns = [

    path('', views.home, name='home'),

    path('register/', views.register, name='register'),

    path('login/', views.user_login, name='login'),

    path('logout/', views.user_logout, name='logout'),

    path('dashboard/', views.dashboard, name='dashboard'),
    path(
    "admin-dashboard/",
    views.admin_dashboard,
    name="admin_dashboard"
    ),
    path(
    "test-email/",
    views.test_email,
    name="test_email",
    ),
    path(
    "customers/",
    views.customer_list,
    name="customer_list",
    ),
    path(
    "customers/<int:pk>/",
    views.customer_detail_admin,
    name="customer_detail_admin",
    ),
]
