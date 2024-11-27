from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/v1/', include("authentication.urls")),

    path('api/v1/', include("users.urls")),
]

if settings.DEBUG: # Apenas para debug = True
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
