from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.exceptions import ImmediateHttpResponse
from allauth.socialaccount.signals import pre_social_login
from allauth.account.models import EmailAddress
from django.contrib.auth import authenticate, login, get_user_model
from allauth.account.utils import perform_login
from allauth.utils import get_user_model
from django.http import HttpResponse
from django.dispatch import receiver
from django.shortcuts import redirect
from django.conf import settings
import json
from django.utils.decorators import method_decorator
from home.utils import persist_session_vars
User = get_user_model()


class MyLoginAccountAdapter(DefaultAccountAdapter):
    """
    Overrides allauth.account.adapter.DefaultAccountAdapter.ajax_response to avoid changing
    the HTTP status_code to 400
    """

    def get_login_redirect_url(self, request):
        """
        """
        if request.user.is_authenticated:
            return settings.LOGIN_REDIRECT_URL.format(id=request.user.id)
        else:
            return "/"


class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin): 
        user = sociallogin.user
        if user.id:  
            return          
        try:
            customer = User.objects.get(email=user.email)  # if user exists, connect the account to the existing account and login
            sociallogin.state['process'] = 'connect'                
            perform_login(request, customer, 'none')
        except User.DoesNotExist:
            pass