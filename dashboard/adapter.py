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
    """
    Overrides allauth.socialaccount.adapter.DefaultSocialAccountAdapter.pre_social_login to
    perform some actions right after successful login
    """

    @method_decorator(persist_session_vars(['ref_user_id']))
    def pre_social_login(self, request, sociallogin):
        print('user', sociallogin.user)
        # sociallogin.leave()
        # pass
        # if ref_user_id:
        #     request.session['ref_user_id'] = ref_user_id
        #     request.session['referred_email'] = sociallogin.user


@receiver(pre_social_login)
def link_to_local_user(sender, request, sociallogin, **kwargs):
    """ Login and redirect
    This is done in order to tackle the situation where user's email retrieved
    from one provider is different from already existing email in the database
    (e.g facebook and google both use same email-id). Specifically, this is done to
    tackle following issues:
    * https://github.com/pennersr/django-allauth/issues/215

    """
    ref_user_id = request.session.get('ref_user_id')
    ref_user = User.objects.get(id=ref_user_id)
    try:
        print('2', request.user)
        print('2', sociallogin.user)
    except:
        pass
    # email = str(sociallogin.account)
    # print('social account', sociallogin.email_addresses)
    # referred_user = User.objects.filter(email=email).first()
    # recomended_by = referred_user.recommended_by
    # if not recomended_by:
    #     referred_user.recommended_by = ref_user
    #     ref_user.days_remaining += 3
    #     ref_user.save()
    #     referred_user.save()
    try:
        pass
        # print('session variable', request.session.get('ref_user_id'))
        # print('user', request.user)
        # ref_user_id = request.session.get('ref_user_id')
        # if ref_user_id:
        #     request.session['ref_user_id'] = ref_user_id
        #     request.session['referred_email'] = sociallogin.user
        # email_address = sociallogin.account.extra_data['elements'][0]['handle~']['emailAddress']
        # code = request.GET.get('code', None)
        # code2 = request.GET.get('AUTH2_AUTHORIZATION_CODE', None)
        # if user:
        #     sociallogin.connect(request, user)
        #     res = ImmediateHttpResponse(redirect(settings.LOGIN_REDIRECT_URL.format(id=request.user.id)))
        #     raise res
    except Exception as error:
        return HttpResponse(str(error))
