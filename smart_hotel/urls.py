


from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('booking/', include('booking.urls')),
    path('rooms/', include('rooms.urls')),
    path('feedback/', include('feedback.urls')),
    path('reports/', include('reports.urls')),
    path('staff/', include('staff.urls')),
    path("payment/", include("payments.urls")),
    path("customer/", include("customer.urls")),
    path('ai-concierge/', include('ai_concierge.urls')),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
