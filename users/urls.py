from django.urls import path
from .views import ShowProfilePageView,EditProfilePageView,EditProfileSettingsView

urlpatterns = [
    path('<str:username>/', ShowProfilePageView.as_view(), name='show_profile_page'),
    path('<str:username>/edit_profile_page/', EditProfilePageView.as_view(), name='edit_everave_profile'),
    path('<str:username>/edit_profile_settings/', EditProfileSettingsView.as_view(), name='edit_everave_profile_settings'),
    # path('<str:username>/edit-profile/tab-1', EditProfileSettingsView.as_view(), name='edit_everave_profile_settings'),
    # path('<str:username>/edit-profile/tab-2', EditProfileSettingsView.as_view(), name='edit_everave_profile_settings'),

    ]
