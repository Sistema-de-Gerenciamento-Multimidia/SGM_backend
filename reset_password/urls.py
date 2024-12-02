from django.urls import path
from .views import PasswordResetRequestView, PasswordResetConfirmationView


urlpatterns = [
    path('reset-password/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('reset-password/confirm/<str:token>/', PasswordResetConfirmationView.as_view(), name='password-reset-confirmation')
]

