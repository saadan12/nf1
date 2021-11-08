import time
import pytz
import requests
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from currency_converter import CurrencyConverter
from django.shortcuts import render, redirect, HttpResponse
from django.core.cache import cache
from django.db.models import Q
from binance.client import Client
from binance.exceptions import BinanceAPIException

from home.models import Post,Category
from users.models import AllLogin, UserActivity
from users.models import Privacy_Policy, Cookies_Policy, API_KEY, AuthCode
from .middleware import get_ip_and_location
from django.utils import translation
from allauth.socialaccount.views import ConnectionsView
from allauth.socialaccount.models import SocialAccount
from django.urls import reverse, reverse_lazy
from django.contrib.auth import login

from django.contrib.auth import logout
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import activate, get_language
from django.utils.translation import gettext as _
from home.utils import generate_ref_code
from home.views import deploy
from users.models import CustomUser
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

c = CurrencyConverter()
User = get_user_model()

limit_list = list()
for i in range(1, 11):
    limit_list.append(i * 100)

generic_context = {
    'limit_list': limit_list,
    'tab': 'trade',
}


def create_login_session(request):
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
    key_ip_stack = 'ff45da09c258af9a24613df6a97af897'
    url = f"http://api.ipstack.com/{ip}?access_key={key_ip_stack}"
    response = requests.get(url)
    response.raise_for_status()
    r = response.json()
    # print('r', r)
    city = r['city']
    country = r['country_name']

    browser = f"{browser} ({operating_system})"
    near = f"{city}, {country}"
    if near == "None, None":
        near = "Unknown"

    ip_current = ip.split(".")
    ip_current = ip_current[0] + "." + ip_current[1]
    objs = AllLogin.objects.filter(user=request.user, ip_address__startswith=ip_current, near=near, browser=browser)
    if objs:
        obj = objs.first()
        obj.ip_address = ip
        obj.save()
    else:
        obj = AllLogin.objects.create(user=request.user, browser=browser, ip_address=ip, near=near)
    return obj


class CustomConnections(ConnectionsView):
    success_url = reverse_lazy("socialaccount_connections1")
    # success_url = "http://localhost:8000/account/social/connections"

    def get_context_data(self, **kwargs):
        ret = super(CustomConnections, self).get_context_data(**kwargs)
        user = self.request.user
        social_accounts = SocialAccount.objects.filter(user=user)
        provider_list = []
        for account in social_accounts:
            provider_list.append(account.provider)
        ret['provider_list'] = provider_list
        ret['url'] = super(CustomConnections, self).get_success_url()
        return ret

    # def get_success_url(self):
    #     return reverse_lazy("socialaccount_connections1")


def set_btc_session(req=None, client=None):
    user = req.user
    client = client
    if not client:
        req.session['btc_amount'] = float('0.0')
        req.session['btc_balance'] = float('0.0')
    else:
        url = "https://api.binance.com/api/v3/ticker/price?symbol="
        bal_dict = dict()
        spot_balance = client.get_account()['balances']
        for item in spot_balance:
            amount = float(item['free'])
            asset = item['asset']
            locked = float(item['locked'])
            if amount > 0:
                bal_dict[asset] = amount + locked

        futures_balance = client.futures_account_balance()
        for item in futures_balance:
            amount = float(item['balance'])
            asset = item['asset']
            if amount > 0:
                if asset in bal_dict:
                    bal_dict[asset] += amount
                else:
                    bal_dict[asset] = amount
        total_bal = 0
        for symbol in bal_dict:
            if symbol == 'USDT':
                amount = bal_dict[symbol]
            else:
                price = requests.get(url + symbol + 'USDT').json()['price']
                price = float(price)
                amount = price * bal_dict[symbol]
            total_bal += amount
        price_btc = requests.get(url + "BTCUSDT").json()['price']
        price_btc = float(price_btc)
        total_btc = 1 / price_btc * total_bal
        total_btc = round(total_btc, 7)

        if user.default_currency != 'USD':
            total_bal = c.convert(total_bal, 'USD', user.default_currency)
        total_bal = round(total_bal, 2)
        req.session['btc_amount'] = total_btc
        req.session['btc_balance'] = total_bal
    return 'session vars set for btc amount and balance'


def privacy_policy(request):
    # activate('ru')
    # request.session[translation.LANGUAGE_SESSION_KEY] = 'ru'
    # request.session['language'] = 'ru'
    privacy_obj = Privacy_Policy.objects.all()
    privacy = None
    if privacy_obj:
        privacy = privacy_obj.first().privacy_content

    context = {
        'privacy_policy': privacy,
    }
    return render(request, 'footer_docs/privacy_policy.html', context=context)


def cookies_policy(request):
    cookies_obj = Cookies_Policy.objects.all()
    cookies = None
    if cookies_obj:
        cookies = cookies_obj.first().cookies_content
    context = {
        'cookies_policy': cookies,
    }
    return render(request, 'footer_docs/cookies_policy.html', context=context)


class ProfileView:
    @login_required()
    def Trade(request):
        try:
            user = request.user
            api_objs = API_KEY.objects.filter(user=user)
            client = None
            if api_objs:
                api_obj = api_objs.first()
                api_key = api_obj.public_key
                api_secret = api_obj.secret_key
                client = Client(api_key, api_secret)
            set_btc_session(req=request, client=client)

            if client:
                # close_position = client.futures_cancel_order(symbol="LTCUSDT")
                positions = client.futures_position_information()
                position_list = list()
                if positions:
                    tp = '--'
                    sl = '--'
                    for position in positions:
                        # notify for tp, sl execution
                        try:
                            if position['stopPrice']:
                                stopPrice = float(position['stopPrice'])
                                sl = round(stopPrice, 2)
                            if position['unrealizedProfit']:
                                take_profit = float(position['unrealizedProfit'])
                                tp = round(take_profit, 2)
                            if position['totalUnrealizedProfit']:
                                take_profit = float(position['totalUnrealizedProfit'])
                                tp = round(take_profit, 2)
                        except:
                            pass

                        entry_price = float(position['entryPrice'])
                        mark_price = float(position['markPrice'])
                        size = float(position['positionAmt'])

                        if entry_price > 0 and mark_price > 0 and size > 0:
                            symbol = position['symbol']
                            leverage = float(position['leverage'])
                            from_symbol = client.get_symbol_info(symbol)['baseAsset']
                            to_symbol = client.get_symbol_info(symbol)['quoteAsset']
                            # symbol = s[:-4]
                            liq_price = position['liquidationPrice']
                            # liq_price = round(float(liq_price), 2)
                            margin1 = entry_price*size/leverage
                            margin = round(margin1, 2)
                            pnl1 = (size * mark_price) - (size * entry_price)
                            pnl = round(pnl1, 2)
                            ROI = pnl1/margin1 * 100
                            ROI = round(ROI, 2)
                            position_list.append([symbol, f"{size} {from_symbol}", entry_price, mark_price,
                                                  liq_price, f"{margin} {to_symbol}", pnl, ROI, f"{tp}/{sl}"])

                            # Notify for futures position(tp/sl)
                            order_notified = request.session.get(f"symbol: {symbol}")
                            if not order_notified:
                                msg = _(f"Futures Position {symbol}(size: {size}) was executed.")
                                messages.success(request, msg)
                                request.session[f"symbol: {symbol}"] = symbol

                open_orders_futures = list()
                # [date, symbol, type, side, price,amount,filled]
                if client.futures_get_open_orders():
                    for item in client.futures_get_open_orders():
                        order_id = item['orderId']
                        type = item['type']
                        origQty = item['origQty']
                        executedQty = item['executedQty']

                        # Notify for futures open order executed
                        order_notified = request.session.get(f"order id: {order_id}")
                        if float(item['executedQty']) > 0 and not order_notified:
                            msg = _(f"Futures Order {item['symbol']}(Type: {type}) was executed. Original Quantity: {origQty}, Executed Quantity: {executedQty}")
                            messages.success(request, msg)
                            request.session[f"order_id: {order_id}"] = order_id

                        if type == 'LIMIT':
                            order_date = time.strftime("%d %b %Y", time.localtime(item['time'] / 1000))
                            side = item['side']
                            order_type = item['type']
                            symbol = item['symbol']
                            # trade_fee = client.get_trade_fee(symbol=symbol)[0]
                            # trade_fee = float(trade_fee['makerCommission']) + float(trade_fee['takerCommission'])
                            price = item['price']
                            amount = item['origQty']
                            filled = item['executedQty']
                            symbol2 = client.get_symbol_info(symbol)['baseAsset']
                            # remaining_balance = client.get_asset_balance(symbol)['free']
                            open_orders_futures.append(
                                (order_date, symbol, order_type, side, price, f"{amount} {symbol2}", f"{filled} {symbol2}"))
                currency = user.default_currency
                if currency != 'USD':
                    i = 0
                    for p in position_list:
                        entry_price = p[2]
                        mark_price = p[3]
                        liq_price = p[4]
                        entry_price = c.convert(entry_price, 'USD', currency)
                        mark_price = c.convert(mark_price, 'USD', currency)
                        liq_price = c.convert(liq_price, 'USD', currency)
                        entry_price_new = round(entry_price, 2)
                        mark_price_new = round(mark_price, 2)
                        liq_price_new = round(liq_price, 2)
                        p[2] = entry_price_new
                        p[3] = mark_price_new
                        p[4] = liq_price_new
                        i += 1

                context = {
                    'position_list': position_list,
                    'tab': 'trade',
                    'open_orders_futures': open_orders_futures,
                    'limit_list': limit_list,
                }
                return render(request, 'home/trade.html', context)
                # return render(request, 'charting-library/chart.html', context)
            else:
                generic_context['no_keys'] = True
                messages.success(request, _("Please add the api keys for your binance account"))
            return render(request, 'home/trade.html', generic_context)
        except BinanceAPIException as e:
            print('error_code', e.code)
            print('error_msg', e.message)
            if e.code == -2015:
                generic_context['error_code'] = str(e.code)
                msg = _("Invalid api keys, IP or permissions for action.")
                messages.success(request, msg)
                return render(request, 'home/trade.html', generic_context)

            messages.warning(request, e.message)
            return render(request, 'home/trade.html', generic_context)

    @login_required()
    def SettingsApi(request):
        objects = API_KEY.objects.filter(user=request.user)
        context = {
            'key_objects': objects,
        }
        return render(request, 'profile/settings-api.html', context)

    @login_required()
    def SettingsApplication(request):
        context = {
            'timezones': pytz.common_timezones,
        }
        return render(request, 'profile/settings-application.html', context)

    @login_required()
    def SettingsFees(request):
        context = {
            'timezones': pytz.common_timezones,
        }
        return render(request, 'profile/settings-fees.html', context)

    @login_required()
    def SettingsPaymentMethod(request):
        user = request.user
        # create stripe customer if doesn't exist one
        if not user.stripe_id:
            customer = stripe.Customer.create(
                email=user.email,
                name=user.first_name
            )
            user.stripe_id = customer['id']
            user.save()

        context = dict()
        if request.method == 'POST':
            name = request.POST.get('name')
            card_no = request.POST.get('card_no')
            expiry = request.POST.get('expiry')
            exp_month, exp_year = expiry.split('/')
            cvc = request.POST.get('cvc')

            try:
                payment_method = stripe.PaymentMethod.create(
                    type="card",
                    card={
                        "number": card_no,
                        "exp_month": exp_month,
                        "exp_year": exp_year,
                        "cvc": cvc,
                    },
                )
                payment_method_id = payment_method['id']

                payment_attached = stripe.PaymentMethod.attach(
                    payment_method_id,
                    customer=user.stripe_id,
                )
                brand = payment_attached['card']['brand']
                brand = brand.capitalize()
                context['payment_added'] = True
                messages.success(request, _(f"Payment method({brand}) added successfully!"))
            except stripe.error.CardError as e:
                print("stripe_http_status", e.http_status)
                print("stripe_error_code", e.code)
                print("stripe_message", e.user_message)
                if int(e.http_status) != 200:
                    context['payment_added'] = True
                    context['stripe_message'] = e.user_message

        methods = stripe.PaymentMethod.list(
            customer=user.stripe_id,
            type="card",
        )
        context['timezones'] = pytz.common_timezones
        context['payment_methods'] = methods
        return render(request, 'profile/settings-payment-method.html', context)

    @login_required()
    def SettingsPrivacy(request):
        context = {
            'timezones': pytz.common_timezones,
        }
        return render(request, 'profile/settings-privacy.html', context)

    @login_required()
    def SettingsSecurity(request):
        context = {
            'timezones': pytz.common_timezones,
        }
        return render(request, 'profile/settings-security.html', context)

    @login_required()
    def ProfileActivity(request):
        # print("USER ID ", str(request.user.id))
        logged_in_user_posts = Post.objects.filter(author=request.user)
        logged_in_user_liked_posts = User.objects.prefetch_related('blog_post').get(pk=request.user.id).blog_post.all()
        # print("LIKE PROFILE", logged_in_user_liked_posts)
        # logged_in_user_liked_posts = User.objects.get(pk=1).blog_post.all()
        # print("POSTS ", User.objects.prefetch_related('blog_post').get(pk=1).blog_post.all())
    #     def get_context_data(self, *args, **kwargs):
    #
    #         cat_menu = Category.objects.all()
    #         context = super(ArticleDetailView, self).get_context_data(*args, **kwargs)
    #
    #
    #         stuff = get_object_or_404(Post, asset_slug=self.kwargs['asset_slug'])
    #         # print("stuff", stuff.author)
    #         total_likes = stuff.total_likes()
    #
    #         # print(self.args['author'])
    #         get_author_data = stuff.author_data()
    #         get_author_data = User.objects.get(id=get_author_data)
    #         print('stuff',get_author_data.image.url)
    #
    #         liked = False
    #         if stuff.likes.filter(id=self.request.user.id).exists():
    #             liked = True
    # # .image.url
    #         context['cat_menu'] = cat_menu
    #         context['total_likes'] = total_likes
    #         context['liked'] = liked
    #         context['author_data'] = get_author_data
    #         return context
        context = {
            'logged_in_user_posts':logged_in_user_posts,
            'logged_in_user_liked_posts':logged_in_user_liked_posts,
        }
        return render(request, 'alt_profile/profile.html', context)

    @login_required()
    def AddAsset(request):
        context = {
        }
        return render(request, 'alt_profile/add_asset.html', context)

    @login_required()
    def SettingsProfile(request):
        try:
            user = request.user
            api_objs = API_KEY.objects.filter(user=user)
            client = None
            if api_objs:
                api_obj = api_objs.first()
                api_key = api_obj.public_key
                api_secret = api_obj.secret_key
                client = Client(api_key, api_secret)

            if deploy:
                set_btc_session(req=request, client=client)

            context = {
            }
            msg_no_api = _("Please add the api keys for your binance account")
            if not client:
                messages.success(request, msg_no_api)
            return render(request, 'profile/settings-profile.html', context)
        except BinanceAPIException as e:
            print('error_code', e.code)
            print('error_msg', e.message)
            if e.code == -2015:
                msg = _("Invalid api keys, IP or permissions for action.")
                messages.success(request, msg)
                return render(request, 'profile/settings-profile.html', {})
            messages.warning(request, e.message)
            return render(request, 'profile/settings-profile.html', {})

    @login_required()
    def SettingsActivity(request):
        # Getting login sessions
        login_sessions = AllLogin.objects.filter(user=request.user)
        activities = UserActivity.objects.filter(user=request.user).order_by('-when')[:20]
        # ip = near = browser = obj = None
        current_session_id = None
        try:
            ip, near, browser = get_ip_and_location(request, get_browser=True)
            ip_current = ip.split(".")
            ip_current = ip_current[0] + "." + ip_current[1]
            obj = AllLogin.objects.filter(user=request.user, ip_address__startswith=ip_current, near=near, browser=browser)
            print(obj)
            if obj:
                current_session_id = int(obj.first().id)
                print('current_session_id', current_session_id)
        except:
            pass
        context = {
            'login_sessions': login_sessions,
            'activities': activities,
            'current_session_id': current_session_id,
        }
        return render(request, 'profile/settings-activity.html', context)

    def Blank(request):
        context = {'div1': 'Hello'}
        return render(request, 'home/blank.html', context)

    def Intro(request):
        context = {'div1': 'Hello'}
        return render(request, 'home/intro.html', context)

    def Lock(request):
        context = {'div': 'Hello'}
        return render(request, 'home/lock.html', context)

    def Otp1(request):
        context = {'div': 'Hello'}
        return render(request, 'home/otp-1.html', context)

    def Otp2(request):
        context = {'div': 'Hello'}
        return render(request, 'home/otp-2.html', context)

    def PriceDetails(request):
        context = {'div': 'Hello'}
        return render(request, 'home/price-details.html', context)

    def Price(request):
        context = {'div': 'Hello'}
        return render(request, 'home/price.html', context)

    def Reset(request):
        context = {'div': 'Hello'}
        return render(request, 'home/reset.html', context)

    def SignIn(request):
        context = {'div': 'Hello'}
        return render(request, 'home/signin.html', context)

    def SignUp(request):
        context = {'div': 'Hello'}
        return render(request, 'home/signup.html', context)

    def VerifyEmail(request):
        context = {'div': 'Hello'}
        return render(request, 'home/verify-email.html', context)

    @login_required()
    def Wallet(request):
        refferals = User.objects.filter(recommended_by=request.user)
        context = {
            'refferals': refferals,
        }
        return render(request, 'home/wallet.html', context)


def add_keys(request):
    public_key = request.POST.get('public_key')
    secret_key = request.POST.get('secret_key')
    exchange = request.POST.get('exchange')
    objects = API_KEY.objects.filter(user=request.user)

    # check if the keys already exist
    public_key_exist = API_KEY.objects.filter(Q(public_key=public_key) | Q(secret_key=public_key) & ~Q(user=request.user))
    secret_key_exist = API_KEY.objects.filter(Q(public_key=secret_key) | Q(secret_key=secret_key) & ~Q(user=request.user))

    if public_key_exist or secret_key_exist:
        print('These API Keys are associated with another account!')
        msg = _("These API Keys are associated with another account!")
        context = {
            'key_objects': objects,
            'msg': msg,
        }
        return render(request, 'profile/settings-api.html', context)

    if secret_key_exist:
        print('key already exist')
        msg = _("Secret Key Already Exists!")
        context = {
            'key_objects': objects,
            'msg': msg,
        }
        return render(request, 'profile/settings-api.html', context)

    # Cannot add more then one key
    if objects:
        print('Cannot add more then one API key!')
        msg = _("Cannot add more then one API key!")
        context = {
            'key_objects': objects,
            'msg': msg,
        }
        return render(request, 'profile/settings-api.html', context)

    API_KEY.objects.create(user=request.user, public_key=public_key, secret_key=secret_key, exchange=exchange)
    msg = _('The API Keys are Added and encrypted successfully!.')
    messages.success(request, msg)
    return redirect('settings-api')


def delete_api_keys(request):
    obj_id = request.POST.get('id')
    api_key_obj = API_KEY.objects.get(id=obj_id)
    exchange = api_key_obj.exchange
    api_key_obj.delete()
    msg_delete_keys = _(f"API Keys for {exchange} exchange Deleted Successfully!")
    messages.success(request, msg_delete_keys)
    return redirect('settings-api')


def white_paper(request):
    return render(request, 'footer_docs/whitepaper.html', {})


def faq(request):
    return render(request, 'footer_docs/faq.html', {})


def confirm_login(request):
    msg = None
    if request.method == 'POST':
        code = request.POST.get('code')
        users = CustomUser.objects.filter(login_code=code)
        if users:
            response = redirect('settings-profile')
            user = users.first()
            cache.set('auth_code', code)
            request.session['auth_code'] = code
            login(request, user, backend=settings.AUTHENTICATION_BACKENDS[0])
            create_login_session(request)
            messages.success(request, _(f"Successfully Signed In As {user.email}"))
            return response
            # cache.set('auth_code', code)
            # request.session['auth_code'] = code
            # response = render(request, 'confirm_login_success.html', {})
            # response.set_cookie('auth_code', code)
            # return response
        else:
            msg = _("The Code is Invalid")

    context = {
        'msg': msg
    }
    return render(request, 'confirm-login.html', context)

def new_login_session(request):
    msg = None
    if request.method == 'POST':
        code = request.POST.get('code')
        users = CustomUser.objects.filter(login_code=code)
        if users:
            response = redirect('settings-profile')
            user = users.first()
            cache.set('auth_code', code)
            request.session['auth_code'] = code
            login(request, user, backend=settings.AUTHENTICATION_BACKENDS[0])
            create_login_session(request)
            messages.success(request, _(f"Successfully Signed In As {user.email}"))
            return response
            # cache.set('auth_code', code)
            # request.session['auth_code'] = code
            # response = render(request, 'confirm_login_success.html', {})
            # response.set_cookie('auth_code', code)
            # return response
        else:
            msg = _("The Code is Invalid")

    context = {
        'msg': msg
    }
    return render(request, 'confirm-login.html', context)
