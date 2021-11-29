from django.urls import path
from .views import CreateCheckoutSessionView, UserRegisterView, logout_view
from . import views

urlpatterns = [
    path('create-checkout-session/<pk>/', CreateCheckoutSessionView.as_view(),name="create-checkout-session"),
    path('success/',views.confirm_payment, name="success"),
    path('cancel/',views.cancel_payment, name="cancel"),
    path('register/', UserRegisterView.as_view(), name='register'),
    path('logout/', logout_view, name='logout'),
]
