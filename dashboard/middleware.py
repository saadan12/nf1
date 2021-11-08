import requests
from users.models import UserActivity, AllLogin
from django.core.cache import cache
from django.shortcuts import render, redirect


class CustomMiddleware(object):
    def __init__(self, get_response):
        """
        One-time configuration and initialisation.
        """
        # print('get_response', get_response)
        self.get_response = get_response

    def __call__(self, request):
        """
        Code to be executed for each request before the view (and later
        middleware) are called.
        """
        response = self.get_response(request)
        # print('response', response)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Called just before Django calls the view.
        """
        # print('view_func', dir(view_func))
        # print('view_args', view_args)
        # print('view_kwargs', view_kwargs)
        url = str(request.build_absolute_uri())
        if url.endswith('accounts/social/connections/'):
            return redirect('socialaccount_connections1')
        # print('name', view_func.__name__)
        # delete login session object on logout
        func_name = view_func.__name__  # p, near , browser
        if func_name == 'LogoutView':
            try:
                ip, near, browser = get_ip_and_location(request, get_browser=True)
                obj = AllLogin.objects.filter(user=request.user, near=near, ip_address=ip, browser=browser)
                if obj:
                    signin_obj_id = obj.first().id
                    cache.set('signin_obj_id', signin_obj_id)
            except:
                pass
        signin_obj_id = cache.get('signin_obj_id')
        if func_name == 'LoginView' and signin_obj_id:
            # AllLogin.objects.get(id=signin_obj_id).delete()
            cache.delete('signin_obj_id')

        # print('methods', dir(request))
        messages = request._messages
        if messages and request.user.is_authenticated and not request.user.is_superuser:
            # Getting Source
            device_family = request.user_agent.device.family  # returns 'iPhone'
            device = None
            if request.user_agent.is_mobile:
                device = 'Mobile'
            elif request.user_agent.is_tablet:
                device = 'Tablet'
            elif request.user_agent.is_pc:
                device = 'Pc'
            elif request.user_agent.is_bot:
                device = 'Bot'

            if device_family.lower() == 'other':
                source = device
            else:
                source = f"{device} ({device_family})"
            for msg in messages:
                try:
                    ip, location = get_ip_and_location(request)
                    if location == 'None, None':
                        location = 'Unknown'
                    UserActivity.objects.create(user=request.user, ip_address=ip, location=location, action=msg,
                                                source=source)
                except:
                    pass
        # print('create_login_session', create_login_session(request))
        return None

    def process_exception(self, request, exception):
        """
        Called when a view raises an exception.
        """
        print('exception', exception)
        return None

    def process_template_response(self, request, response):
        """
        Called just after the view has finished executing.
        """
        # print('user', request.user)
        return response


def get_ip_and_location(request, get_browser=None):
    # geting the browser & operating system
    browser = request.user_agent.browser.family
    operating_system = request.user_agent.os.family

    # getting the user's ip and location
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        # ip = request.META.get
        ip = request.META.get('REMOTE_ADDR')

    # ip = '103.255.6.250'
    key_ip_stack = 'b6ed12e1ab50babb9574d9d3bd5ceae4'
    url = f"http://api.ipstack.com/46.199.192.135?access_key={key_ip_stack}"
    response = requests.get(url)
    response.raise_for_status()
    r = response.json()
    print(r)
    # try:
    city = r['city']
    country = r['country_name']
    browser = f"{browser} ({operating_system})"
    location = f"{city}, {country}"
    near = f"{city}, {country}"
    if near == 'None, None':
        near = 'Unknown'
    if get_browser:
        return [ip, near, browser]
    return [ip, location]
    # except:
    #     return ['12', 'london', "Safari"]
