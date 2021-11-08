"""dashboard URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.views.generic import RedirectView
from django.shortcuts import redirect

from django.urls import reverse, reverse_lazy


from home.views import (
    account_confirm_email_custom, charting_library, get_levels, update_profile
)
from .views import privacy_policy, cookies_policy, ProfileView, add_keys, delete_api_keys, faq, white_paper, confirm_login
from .views import CustomConnections

urlpatterns = [
    # path('books/', include('home.urls'), name='books'),
    path('admin/', admin.site.urls),
    path('', include(('home.urls', 'home'), namespace = 'home')),
    path('users/', include(('users.urls', 'users'), namespace = 'users')),
    path('members/', include('django.contrib.auth.urls')),
    path('members/', include('members.urls')),
    path('accounts/', include('allauth.urls')),
    path('confirmed/<str:key>', account_confirm_email_custom.as_view(), name='account_confirm_email_custom'),
    path('i18n/', include('django.conf.urls.i18n')),
    # path('graph/', charting_library),
    # path('get-levels/<str:symbol>/<str:interval>/<str:limit>', get_levels, name='get_levels'),
    path('privacy-policy', privacy_policy, name='privacy_policy'),
    path('cookies-policy', cookies_policy, name='cookies_policy'),
    # path('<str:username>/', ProfileView.ProfileActivity, name='profile'),
    path('add-asset/', ProfileView.AddAsset, name='add_asset'),
    path('settings-profile/', ProfileView.SettingsProfile, name='settings-profile'),
    path('update-profile', update_profile, name='update_profile'),
    path('settings-activity/', ProfileView.SettingsActivity, name='settings-activity'),
    path('settings-api/', ProfileView.SettingsApi, name='settings-api'),
    path('settings-application/', ProfileView.SettingsApplication, name='settings-application'),
    path('settings-fees/', ProfileView.SettingsFees, name='settings-fees'),
    path('settings-payment-method/', ProfileView.SettingsPaymentMethod, name='settings-payment-method'),
    path('settings-privacy/', ProfileView.SettingsPrivacy, name='settings-privacy'),
    path('settings-security/', ProfileView.SettingsSecurity, name='settings-security'),
    # path('add-keys', add_keys, name='add_keys'),
    # path('delete-keys', delete_api_keys, name='delete_api_keys'),
    path('white-paper', white_paper, name='white_paper'),
    path('FAQ', faq, name='faq'),
    path('confirm-login', confirm_login, name='confirm_login'),
    path('account/social/connections', CustomConnections.as_view(), name='socialaccount_connections1'),
    path('accounts/social', RedirectView.as_view(pattern_name='white_paper')),
    path('tinymce/', include('tinymce.urls')),
]


handler404 = 'home.views.custom_page_not_found_view'
handler500 = 'home.views.custom_error_view'
handler403 = 'home.views.custom_permission_denied_view'
handler400 = 'home.views.custom_bad_request_view'
#
urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
# necessary if you  want to serves media files locally
urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG: # new
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += [
        path('rosetta/', include('rosetta.urls'))
    ]
# from django.contrib.staticfiles.urls import staticfiles_urlpatterns
# urlpatterns += staticfiles_urlpatterns()
