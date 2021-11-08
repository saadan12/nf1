import os
import csv
import time
import math
import json
import glob
import pytz
import hmac
import jsonpickle
import requests
from django.core.exceptions import MultipleObjectsReturned
import hashlib
import datetime
from datetime import timedelta
from datetime import date as date_current
import binance
from lxml.html import fromstring
from django.http import HttpResponse, Http404

from home.OpenSea import OpenSea


from binance.client import Client
from django.contrib.auth.decorators import login_required
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.models import SocialToken, SocialApp
from allauth.account.views import ConfirmEmailView
from binance.exceptions import BinanceAPIException
from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import logout

from allauth.account.views import LoginView
from balances.models import CoinBalance, Coin
from django.contrib.auth import get_user_model
from datetime import date
from django.db.models import Max
from users.models import CustomUser, API_KEY, AuthCode
from django.utils import translation
from django.utils.translation import gettext as _
from django.utils.translation import activate, get_language
from currency_converter import CurrencyConverter

from xml.etree import ElementTree
from xml.dom import minidom
from django.http import HttpResponse
from wsgiref.util import FileWrapper  # this used in django
from mimetypes import guess_type
from django.core.cache import cache
from django.db.models import Q
from django.contrib.auth import login

from home.to_send_levels_tv import get_levels_coin, get_request_df
from users.forms import ProfileForm
from users.models import CustomUser, AllLogin
from balances.models import Coin
from django.conf import settings
from django.contrib.staticfiles.views import serve
import stripe
from dashboard.middleware import get_ip_and_location
from django.core.mail import send_mail
stripe.api_key = settings.STRIPE_SECRET_KEY

# =======================================================
from io import BytesIO
# from xhtml2pdf import pisa
from django.template.loader import get_template, render_to_string
from .utils import generate_ref_code, generic_context, HomeModules

# ==========================INFIL========================

from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Post, Category,OpenSeaAsset
from .forms import PostForm,EditForm,FileUploadForm,OriginAddAssetForm
from django.urls import reverse_lazy,reverse
from django.http import HttpResponseRedirect
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import FormView, CreateView, UpdateView
# from books.models import Books
# from . forms import AddForm
from django.db.models import F
from django.utils import timezone
# from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect
opensea_client = OpenSea()



def custom_page_not_found_view(request, exception):
    return render(request, "errors/404.html", {})

def custom_error_view(request, exception=None):
    return render(request, "errors/500.html", {})

def custom_permission_denied_view(request, exception=None):
    return render(request, "errors/403.html", {})

def custom_bad_request_view(request, exception=None):
    return render(request, "errors/400.html", {})



class UserAccessMixin(PermissionRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if (not self.request.user.is_authenticated):
            return redirect_to_login(self.request.get_full_path(),
                                     self.get_login_url(), self.get_redirect_field_name())
        if not self.has_permission():
            return redirect('/')

        return super(UserAccessMixin, self).dispatch(request, *args, **kwargs)

class HomeView(ListView):
    model = Post
    template_name = 'alt_partials/home.html'
    ordering = ['-post_date']
    context_object_name = 'home_alt'
    # paginate_by = 2
    #
    # response = render(request, 'home.html', {'obj_home':obj_home})
    # return response
    # try:
    # page_url = request.build_absolute_uri()

    def get_context_data(self, *args, **kwargs):
        open_sea_source= opensea_client.GetAssets(limit=20, offset=20)['assets']
        cat_menu = Category.objects.all()
        context = super(HomeView, self).get_context_data(*args, **kwargs)

        for asset in open_sea_source:

            #Write classification first (many to many relationships)
            # for t in asset:
            #     c = Types.objects.get_or_create(name=t)[0]
                #Then insert the article
            try:
                article = OpenSeaAsset.objects.get_or_create(
                contract_address = asset['asset_contract']['address'],
                asset_name = asset['name'],
                asset_token_id = asset['token_id'])[0]
            except:
                post = OpenSeaAsset.objects.filter(
                contract_address = asset['asset_contract']['address'],
                asset_name = asset['name'],
                asset_token_id = asset['token_id'])[0]

        context['cat_menu'] = cat_menu
        context['obj_home'] = open_sea_source
        # context['']
        return context

    # def insertDB(self, *args, **kwargs):
    #     # data = json.load(f)
    #     for asset in open_sea_source:
    #
    #         #Write classification first (many to many relationships)
    #         # for t in asset:
    #         #     c = Types.objects.get_or_create(name=t)[0]
    #             #Then insert the article
    #         article =  OpenSeaAsset.objects.get_or_create(
    #         contract_address = asset['asset_contract']['address'],
    #         asset_name = asset['name'],
    #         asset_token_id = asset['token_id'])


def LikeView(request, asset_slug):
    post = get_object_or_404(Post, asset_slug=request.POST.get("post_id"))
    liked = False
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
    return HttpResponseRedirect(reverse('home:article_detail', args=[str(asset_slug)]))




def CategoryListView(request):
    cat_menu_list = Category.objects.all()
    return render(request, 'alt_partials/category_list.html',{'cat_menu_list':cat_menu_list})

def CategoryView(request, cats):
    category_posts = Post.objects.filter(category__iexact=cats.replace("-", " "))
    return render(request, 'alt_partials/categories.html',{'cats':cats.title().replace('-', ' '), 'category_posts':category_posts})


class ArticleDetailView(DetailView):
    model = Post
    form_class = PostForm
    template_name = 'alt_partials/article_details.html'
    def get_context_data(self, *args, **kwargs):

        cat_menu = Category.objects.all()
        context = super(ArticleDetailView, self).get_context_data(*args, **kwargs)


        stuff = get_object_or_404(Post, asset_slug=self.kwargs['asset_slug'])
        # print("stuff", stuff.author)
        total_likes = stuff.total_likes()

        # print(self.args['author'])
        get_author_data = stuff.author_data()
        get_author_data = User.objects.get(id=get_author_data)
        # print('stuff',get_author_data.image.url)

        liked = False
        if stuff.likes.filter(id=self.request.user.id).exists():
            liked = True
# .image.url
        context['cat_menu'] = cat_menu
        context['total_likes'] = total_likes
        context['liked'] = liked
        context['author_data'] = get_author_data
        return context

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        # print(self.kwargs)
        # try_
        name = self.kwargs['asset_slug'] or self.request.GET.get('asset_slug') or None
        # print(name)
        queryset = queryset.filter(asset_slug=name)
        obj = queryset.get()
        return obj




class ArticleDetailViewOS(DetailView):
    model = OpenSeaAsset
    # form_class = PostForm
    template_name = 'alt_partials/asset_details_os.html'
    def get_context_data(self, *args, **kwargs):

        context = super(ArticleDetailViewOS, self).get_context_data(*args, **kwargs)
        print("ARGS==========>>>",self.args)
        print("KWARGS==========>>>",self.kwargs)

        try:
            post = get_object_or_404(OpenSeaAsset, contract_address=self.kwargs['contract_address'], asset_token_id=self.kwargs['asset_token_id'])
        except:
            post = OpenSeaAsset.objects.filter(contract_address=self.kwargs['contract_address'],asset_token_id=self.kwargs['asset_token_id'])[0]
        # post = get_object_or_404(OpenSeaAsset, contract_address=self.kwargs['contract_address'], asset_token_id=self.kwargs['asset_token_id'])
        print("POST==========>>>",post)
        # try:
        open_sea_asset = opensea_client.SingleAssetInfo(asset_contract_address=post.contract_address, token_id=post.asset_token_id)
        print(open_sea_asset)
        # except:
        #     open_sea_asset = opensea_client.SingleAssetInfo(asset_contract_address=20, token_id=0)

        # print("stuff", stuff.author)
        # total_likes = post.total_likes()

        # print(self.args['author'])

        # liked = False
        # if post.likes.filter(id=self.request.user.id).exists():
        #     liked = True
# .image.url
        context['open_sea_asset'] = open_sea_asset
        context['total_likes'] = 122
        context['liked'] = False
        return context

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        # print(queryset)
        # try_
        contract_address = (self.kwargs['contract_address'] or self.request.GET.get('contract_address') or None)
        asset_token_id = (self.kwargs['asset_token_id'] or self.request.GET.get('asset_token_id') or None)

        queryset = queryset.filter(contract_address=contract_address,asset_token_id=asset_token_id)
        print(queryset)
        # obj = queryset.get()
        obj = OpenSeaAsset.objects.filter(contract_address=contract_address,asset_token_id=asset_token_id)[0]
        print(obj)
        # return obj

class AddPostView(CreateView):
    model = Post
    form_class = FileUploadForm
    template_name = 'alt_partials/add_post.html'
    # fields = '__all__'
    # fields = ('title', 'body')

class OriginAddView(CreateView):
    model = Post
    form_class = OriginAddAssetForm
    template_name = 'alt_partials/add_post_orig.html'

class AddCategoryView(CreateView):
    model = Category
    template_name = 'alt_partials/add_category.html'
    fields = '__all__'




class UpdatePostView(UpdateView):
    model = Post
    form_class = EditForm
    template_name = 'alt_partials/update_post.html'
    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        # print(self.kwargs)
        # try_
        name = self.kwargs['asset_slug'] or self.request.GET.get('asset_slug') or None
        # print(name)
        queryset = queryset.filter(asset_slug=name)
        obj = queryset.get()
        return obj
    # fields = ['title', 'title_tag', 'body']

class DeletePostView(DeleteView):
    model = Post
    template_name = 'alt_partials/delete_post.html'
    success_url = reverse_lazy('home:home')
    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        # print(self.kwargs)
        # try_
        name = self.kwargs['asset_slug'] or self.request.GET.get('asset_slug') or None
        # print(name)
        queryset = queryset.filter(asset_slug=name)
        obj = queryset.get()
        return obj


# def redirect_view(request):
#     response = redirect('books: ex2', permanent=False)
#
#     return response
#
#
# class UserAccessMixin(PermissionRequiredMixin):
#     def dispatch(self, request, *args, **kwargs):
#         if (not self.request.user.is_authenticated):
#             return redirect_to_login(self.request.get_full_path(),
#                                      self.get_login_url(), self.get_redirect_field_name())
#         if not self.has_permission():
#             return redirect('/books')
#
#         return super(UserAccessMixin, self).dispatch(request, *args, **kwargs)
#
#
# class BookEditView(UserAccessMixin, UpdateView):
#     permission_required = ('books.change_books')
#     model = Books
#     form_class = AddForm
#     template_name = 'templates/book/book_add.html'
#     success_url = '/books/'
#
#
# class AddBookView(CreateView):
#     model = Books
#     form_class = AddForm
#     template_name = 'templates/book/book_add.html'
#     success_url = '/books/'
#
#
# class IndexView(ListView):
#
#     model = Books
#     template_name = "book/book_home.html"
#     context_object_name = 'books'
#     paginate_by = 2
#
#     # queryset = Books.objects.all()[:2]
#     # def get_queryset(self):
#     # return Books.objects.all()[:3]
#
#
# class GenreView(ListView):
#     model = Books
#     template_name = 'templates/book/book_home.html'
#     context_object_name = 'books'
#     paginate_by = 1  # Pagination over-write
#
#     def get_queryset(self, *args, **kwargs):
#         return Books.objects.filter(genre__icontains=self.kwargs.get('genre'))
#
#
# class BookDetailView(DetailView):
#
#     model = Books
#     template_name = 'book/book-detail.html'
#     context_object_name = 'book'
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#
#         post = Books.objects.filter(slug=self.kwargs.get('slug'))
#         print(post)
#         post.update(count=F('count') + 1)
#
#         context['time'] = timezone.now()
#
#         return context

# OPEN SEA

opensea_client = OpenSea()






url = "https://api.binance.com/api/v3/ticker/price?symbol="
proxy_url = "https://free-proxy-list.net/"

# Function to find the remaining time
# ========================================================

c = CurrencyConverter()
today = date.today()
date_today = today.strftime("%B %d, %Y")
date_now = date_current.today().isoformat()
User = get_user_model()
base_url = getattr(settings, "BASE_DIR", None)
base_folder = os.path.abspath('static')

deploy = True
# deploy = False
if not deploy:
    import win32api


def remainingTime(h, m):
    # Formula for total remaining minutes
    # = 1440 - 60h - m
    totalMin = 1440 - 60 * h - m

    # Remaining hours
    hoursRemaining = totalMin // 60
    # Remaining minutes
    minRemaining = totalMin % 60
    return hoursRemaining


def get_levels(request, symbol, interval, limit):
    # if symbol.endswith('USD'):
    #     symbol = symbol + 'T'

    try:
        limit = int(limit)
        request_df = get_request_df(symbol, interval, limit)
        levels = get_levels_coin(request_df)
        print(request_df)
        # print('symbol', symbol)
        # print('interval', interval)
        # print('levels', levels)
        # print(levels)
        # key = "188457fcd2d1cbd95bf56e205d46ea3fd6bcbe9945dbb617fcc2cbd2da86c7ec"
        # r = requests.get(f"https://min-api.cryptocompare.com/data/v3/all/exchanges?api_key={key}")
        # print(r.json())
        print(request.headers)
        return JsonResponse(levels, safe=False)
    except Exception as error:
        print('error: ', error)
        return JsonResponse(str(error), safe=False)


def charting_library(request):
    return render(request, 'charting-library/chart.html')


def lib_file(request, filename):
    if deploy:
        # path = str(base_url) + rf"/static/vendor/charting_library_clonned_data/charting_library/{filename}"
        path = rf"../static/vendor/charting_library_clonned_data/charting_library/{filename}"
    else:
        # path = str(base_url) + rf"\static\vendor\charting_library_clonned_data\charting_library\{filename}"
        path = base_folder + rf'\vendor\charting_library_clonned_data\charting_library\{filename}'
    print('path', path)
    return serve(request, path)


def lib_file2(request, filename):
    if deploy:
        # path = str(base_url) + rf"/static/vendor/charting_library_clonned_data/charting_library/bundles/{filename}"
        path = rf"../static/vendor/charting_library_clonned_data/charting_library/bundles/{filename}"
    else:
        # path = str(base_url) + rf"\static\vendor\charting_library_clonned_data\charting_library\bundles\{filename}"
        path = base_folder + rf'\vendor\charting_library_clonned_data\charting_library\bundles\{filename}'
    return serve(request, path)


def generate_csv(request):
    try:
        user = request.user
        csv_columns = [
            'Full Name', 'Email', 'Date Joined',
            'Timezone', 'Default Currency', 'Default Language',
            'Social Accounts', 'Available Balance',
            'Days Left', 'Referrals'
        ]
        no_of_referrals = User.objects.filter(recommended_by=user).count()
        default_language = request.session.get('language')
        available_balance = request.session.get('available_balance')
        available_balance = str(available_balance)
        symbol = str(user.currency_symbol)
        print(symbol)
        data = {
            'Full Name': user.get_full_name(),
            'Email': user.email,
            'Date Joined': user.date_joined,
            'Timezone': user.time_zone,
            'Default Currency': user.default_currency,
            'Default Language': default_language,
            'Social Accounts': 'Google, Facebook',  # fix this
            'Days Left': user.days_remaining,
            'Referrals': no_of_referrals,
        }
        files = glob.glob('templates/csvfiles/*')
        for f in files:
            os.remove(f)

        csv_file = "personal_info.csv"
        file_path = f"home/templates/csvfiles/{csv_file}"

        with open(file_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=csv_columns)
            writer.writeheader()
            writer.writerow(data)

        with open(file_path, 'r') as f:
            wrapper = FileWrapper(f)
            mimetype = 'application/force-download'
            gussed_mimetype = guess_type('.csv')
            if gussed_mimetype:
                mimetype = gussed_mimetype
            response = HttpResponse(wrapper, content_type=mimetype)
            response['Content-Disposition'] = "attachment;filename=%s" % csv_file
            response["X-SendFile"] = csv_file
            return response
    except Exception as error:
        print('error', error)
        return str(error)


def update_preferences(request):
    try:
        tz = request.POST.get('timezone', None)
        currency = request.POST.get('currency', None)
        language = request.POST.get('language', None)
        user = request.user

        if tz == user.time_zone:
            tz = None
        if currency == user.default_currency:
            currency = None

        language_code, language_name = language.split('_')

        lan_code = request.session.get(translation.LANGUAGE_SESSION_KEY)
        lan_name = request.session.get('language')
        if language_name == lan_name and language_code == lan_code:
            language = None

        # print(tz, currency, language)
        if tz:
            user.time_zone = tz
        if currency:
            user.default_currency = currency
            if currency == 'EUR':
                symbol = '€'
            elif currency == 'GBP':
                symbol = '£'
            elif currency == 'RUB':
                symbol = '₽'
            else:
                symbol = '$'
            user.currency_symbol = symbol
        if language:
            language_code, language_name = language.split('_')
            activate(language_code)
            request.session[translation.LANGUAGE_SESSION_KEY] = language_code
            request.session['language'] = language_name

        user.save()
        if tz and language and currency:
            # msg =
            messages.success(request, _('The Timezone, Language and Default currency Changed Successfully!'))
        if tz and language and not currency:
            messages.success(request, _('The Timezone and Language Changed Successfully!'))
        if tz and currency and not language:
            messages.success(request, _('The Timezone and Default Currency Changed Successfully'))
        if currency and language and not tz:
            messages.success(request, _('The Language and Default Currency Changed Successfully'))
        if tz and not language and not currency:
            messages.success(request, _('The Timezone Changed Successfully'))
        if language and not tz and not currency:
            messages.success(request, _('The Default Language Changed Successfully'))
        if currency and not tz and not language:
            messages.success(request, _('Default Currency Changed Successfully'))

        return redirect('settings-application')
        # return render(request, 'home/settings-application.html', context)
    except Exception as error:
        print('error', error)
        return str(error)


def change_email(request):
    try:
        # 'add_email_address',
        # 'emailaddress_set',
        user = request.user
        existing_email = request.POST.get('email')
        new_email = request.POST.get('new_email')
        # Check if a user exists with the new email
        user2 = User.objects.filter(email=new_email).first()
        msg = None
        if existing_email == user.email and existing_email != new_email and not user2:
            user.add_email_address(request, new_email)
            # user.save()
            msg = _("A confirmation email has sent to change the existing email")
            messages.success(request, msg)
        elif existing_email != user.email:
            msg = _("This is not your current email")
        elif new_email == existing_email:
            msg = _("The new and current emails cannot be same")
        else:
            msg = _("A user already exists with the new email")
        # return HttpResponse('yes')
        context = {
            'msg': msg,
        }
        return render(request, 'profile/settings-profile.html', context)
    except Exception as error:
        print('error', error)
        return str(error)


def update_profile(request):
    try:
        if request.method == 'POST':
            # form = ProfileForm(request.POST, request.FILES)  # Gets the uploaded data and maps it to the ProfileForm object
            # if form.is_valid():  # Checks if the uploaded data is valid or not
            #     form.save()  # Saves the uploaded data into our Database model
            user = request.user
            name = request.POST.get('name')
            if name:
                user.first_name = name
                user.last_name = ''
                messages.success(request, _('User Name Updated Successfully!'))
            if request.FILES:
                user.image = request.FILES['image']
                messages.success(request, _('Profile Picture Changed Successfully!'))
            user.save()
            print(user.password)
            return redirect('settings-profile')
        else:
            form = ProfileForm()
    except Exception as error:
        print('error', error)
        return str(error)


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
    url = f"http://api.ipstack.com/46.199.192.135?access_key={key_ip_stack}"
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


def biance_test(request):
    if not deploy:
        api_key = "TtlTZeyNXbxj0F1jFvRQ8yC9MkwyVPvb3GaEzGSki8s3rvU6IHYZjds88gqkdywt"
        api_secret = "KYsXZ2wBeZgP5D7NXFpKttS295s7TfQPLy31FexFuuB05NvmecrUFTZnMqpxgFnP"

        api_key = "sK00AIkcCsonieG6TQA3xuZOMPLQcXKTZ1pcRPKPPtPAkZXS4z5uToSwu78ra8RE"
        api_secret = "LVOVXZchViZEmwVj7VqBmXkNCMa68XQoHNNwhuZokoTnET175PeNkzNeOR7d8VmR"

        # api_key = "X8zT3lGYYWwmrVGuCBfEJQUtAiHH2BI8oVbo2pv92w4LjWWxXrwhPU4IyojQI5uz"
        # api_secret = "U0VEXuMOD33EznT1s5lrjsRaI30Vt5Nt1gRoyYQuUzG2pVSrsORmeMWEGcMHVngx"

        # if not deploy:
        #     response = requests.get(proxy_url)
        #     parser = fromstring(response.text)
        #     proxies = list()
        #     for i in parser.xpath("//tbody/tr")[:10]:
        #         proxy = ":".join([i.xpath(".//td[1]/text()")[0], i.xpath(".//td[2]/text()")[0]])
        #         proxies.append(proxy)
        #
        #     proxies = {
        #         'https': "http://" + proxies[0]
        #     }
        #     print('proxies', proxies)
        #     client = Client(api_key, api_secret, {'proxies': proxies})
        # else:
        #     client = Client(api_key, api_secret)
        client = Client(api_key, api_secret)



        # print(client.get_account())
        # runserver in cmd administrator
        # gt = client.get_server_time()
        # tt = time.gmtime(int((gt["serverTime"]) / 1000))
        # win32api.SetSystemTime(tt[0], tt[1], 0, tt[2], tt[3], tt[4], tt[5], 0)
        # user = request.user
        # ip, near, browser = get_ip_and_location(request, get_browser=True)
        # print(ip, near, browser)
        # symbol_list = list()
        # total_value = 0
        # for item in client.get_account()['balances']:
        #     amount = float(item['free'])
        #     symbol = (item['asset'])
        #     if amount > 0:
        #         # print(symbol, amount)
        #         if symbol == 'USDT':
        #             val = amount
        #             total_value += val
        #         else:
        #             val = float(requests.get(url + symbol + 'USDT').json()['price']) * amount
        #             # total_value += (symbol, amount, val)
        #         # print(symbol, amount, val)
        #         if val > 1:
        #             symbol_list.append(symbol)

        # positions_dict = dict()
        # for symbol in symbol_list:
        #     if symbol != 'USDT':
        #         positions = client.get_all_orders(symbol=symbol + 'USDT')
        #         # positions_dict[symbol] = list()
        #         for position in positions:
        #             status = position['status']
        #             size = float(position['origQty'])
        #             bal = float(client.get_asset_balance(symbol)['free'])
        #             print(symbol, position)
        #             print('\n\n')
        #             # if status == 'FILLED' and size + 0.5 <= bal:
        #             #     print(position)
        #             #     # print(position['executedQty'])
        #                # positions_dict[symbol].append(position)
        # print(positions_dict)

        # for item in client.get_open_orders():
        #     print(item)

        # total_params = f"symbol=BTCUSDT&orderId=6381739988&timestamp={t}"
        # total_params = f"symbol=BTCUSDT&timestamp={gt}"
        # total_params = str.encode(total_params)
        # signature = hmac.new(api_secret, total_params, hashlib.sha256).hexdigest()
        # base_url = "https://fapi.binance.com"
        # base_url = "https://api.binance.com"
        # path = "/fapi/v2/positionRisk"
        # path = "/api/v3/allOrders"
        # path = "/sapi/v1/lending/project/position/list"
        # path = "/api/v3/order"
        # path = "/api/v3/myTrades"
        # path = "/api/v3/openOrders"
        # url = f"{base_url}{path}?symbol=BTCUSDT&orderId=6381739988&timestamp={t}&signature={signature}"
        # url = f"{base_url}{path}?symbol=BTCUSDT&timestamp={t}&signature={signature}"
        # headers = {
        #     'X-MBX-APIKEY': api_key
        # }

        # r = requests.get(url, headers=headers)
        # print('res', r.json())
        # print(client.get_account())
        # for position in r.json():
        #     entry_price = float(position['entryPrice'])
        #     mark_price = float(position['markPrice'])
        #     if entry_price > 0 or mark_price > 0:
        #         print(position)

        # balance = client.get_account()['balances']
        # for item in balance:
        #     amount = float(item['free'])
        #     if amount > 0:
        #         symbol = item['asset']
        #         if symbol != 'USDT':
        #             print(symbol, client.get_all_orders(symbol=symbol+'USDT'))

        # print(requests.get(url + 'BNBUSDT').json()['price'])
        sum_of_cum_quoteQty = 0
        sum_of_excetued = 0
        # for position in client.get_all_orders(symbol='BNBUSDT'):
        #     if position['status'] == 'FILLED':
        #         origQty = float(position['origQty'])
        #         executedQty = float(position['executedQty'])
        #         cum_quoteQty = float(position['cummulativeQuoteQty'])
        #         sum_of_cum_quoteQty += cum_quoteQty
        #         sum_of_excetued += executedQty
        #         print(position)

        # entry_price = sum_of_cum_quoteQty/sum_of_excetued
        # print(entry_price)

        # for order in client.get_open_orders():
        #     if order['status'] != 'FILLED':
        #         print(order)
        # print(client.get_asset_balance('IRIS')['free'])
        # for order in client.get_all_orders(symbol='IRISUSDT'):
        #     if order['status'] == 'FILLED':
        #     # if float(order['executedQty']) > 0:
        #         print(order)
        # print("--------------------------------------")
        # for order in client.get_all_orders(symbol='IOSTUSDT'):
        #     # if order['status'] == 'FILLED':
        #     if float(order['executedQty']) > 0:
        #         print(order)


        # symbols = ['NULSUSDT', 'BTCUSDT']
        # orders = client.get_all_orders(symbol='NULSUSDT')
        # for position in orders:
        #     sm = position['symbol']
        #     size = float(position['origQty'])
        #     executedQty = float(position['executedQty'])
        #     price = float(position['price'])
        #     type = position['type']
        # for item in dir(client):
        #     print(item)
        return HttpResponse("Testing")
    else:
        return HttpResponse('testing')


def daterange(date1, date2):
    for n in range(int((date2 - date1).days) + 1):
        yield date1 + timedelta(n)


def home(request, *args, **kwargs):
    # obj_home = []
    # for i in range(0,10):
    #     obj_home += opensea_client.GetAssets(limit=20, offset=i+2)['assets']

    # print(len(obj_home))
    obj_home= opensea_client.GetAssets(limit=20, offset=0)['assets']
    # try:
    # page_url = request.build_absolute_uri()
    if not request.user.is_authenticated:
        ref_code = str(kwargs.get('ref_code'))
        response = render(request, 'home.html', {'obj_home':obj_home})
        return response

    response = render(request, 'home.html', {'obj_home':obj_home})
    return response

    # except:
    #     print("huy")


def howme(request, *args, **kwargs):
    try:
        # page_url = request.build_absolute_uri()
        if not request.user.is_authenticated:
            ref_code = str(kwargs.get('ref_code'))
            response = render(request, 'home.html', {})
            try:
                user = User.objects.get(code=ref_code)
                # request.session['ref_user_id'] = user.id
                # request.COOKIES['ref_user_id'] = user.id
                # ref_user_id
                cache.set('ref_user_id', user.id)
                response.set_cookie('ref_user_id', user.id)
                print('Cache & Cookie Variable Set', cache.get('ref_user_id'))
            except:
                pass
            return response
            # return redirect('account_login')
        # set btc amount and btc balance session
        user = request.user
        url = "https://api.binance.com/api/v3/ticker/price?symbol="
        api_objs = API_KEY.objects.filter(user=user)
        if api_objs:
            api_obj = api_objs.first()
            api_key = api_obj.public_key
            api_secret = api_obj.secret_key

            res = requests.get(proxy_url)
            parser = fromstring(res.text)
            proxies = list()
            for i in parser.xpath("//tbody/tr")[:10]:
                proxy = ":".join([i.xpath(".//td[1]/text()")[0], i.xpath(".//td[2]/text()")[0]])
                proxies.append(proxy)

            account_info = None
            for proxy in proxies:
                proxies = proxies = {
                    'https': "http://" + proxy,
                    'http': "http://" + proxy
                }
                try:
                    client = Client(api_key, api_secret, {'proxies': proxies})
                    account_info = client.get_account()
                except:
                    client = Client(api_key, api_secret)
                print('proxy', proxy)
                if account_info:
                    break

            print('account_info', account_info)
            currency_symbol = user.currency_symbol
            currency = user.default_currency
            # if not deploy:
                # gt = client.get_server_time()
                # tt = time.gmtime(int((gt["serverTime"]) / 1000))
                # win32api.SetSystemTime(tt[0], tt[1], 0, tt[2], tt[3], tt[4], tt[5], 0)

            # ================= Balance & Analytics ===================
            # graph_balance_dict to add graph balance for every coin
            fees = 0
            spot_loss = 0
            spot_profit = 0
            opening_cost = 0
            spot_used_margin = 0
            current_valuation = 0
            today_trade_volume = 0
            locked_balance_spot = 0
            symbol_dict = dict()
            balance_list = list()
            spot_positions_dict = dict()
            graph_balance_dict = dict()
            balance = client.get_account()['balances']
            if balance:
                for item in balance:
                    symbol = item['asset']
                    locked_bal = float(item['locked'])
                    amount = float(item['free'])
                    if locked_bal > 0:
                        if symbol == 'USDT':
                            locked_balance_spot += locked_bal
                        else:
                            pr = float(requests.get(url + symbol + 'USDT').json()['price'])
                            locked = pr * locked_bal
                            locked_balance_spot += locked

                    if amount > 0:
                        if symbol == 'USDT':
                            symbol_price = amount
                            value = amount
                        else:
                            symbol_price = float(requests.get(url + symbol + 'USDT').json()['price'])
                            value = float(symbol_price) * amount
                        if value > 1:
                            symbol_dict[symbol] = [symbol_price, round(amount, 6), round(value, 2)]

                        # create symbol object if doesn't exist one
                        coin_obj = Coin.objects.filter(name=symbol)
                        if not coin_obj:
                            Coin.objects.create(name=symbol)

                HomeModules.spot_positions_dict(request, client, symbol_dict, spot_positions_dict)
                # [asset, size, multiple, executedQty, type, tp, sl]

                # today trade volume, used margin
                HomeModules.trade_vol(request, client, symbol_dict, spot_used_margin)

                HomeModules.graph_bal(request, client, symbol_dict,  balance_list)
            # ============  spot_positions_l, position valuation  ===========
            spot_positions_l, current_valuation, opening_cost, spot_profit, spot_loss = \
                HomeModules.spot_positions(request, client, symbol_dict, spot_positions_dict, current_valuation,
                                           opening_cost, spot_profit, spot_loss)

            # ========== spot_balance, label_list, item_percentages, color_list ==========
            spot_balance, label_list, item_percentages, color_list = \
                HomeModules.labels_colors_percents(request, client, balance_list)

            # ================= Trade Balances =====================
            # spot_balance already calculated
            # Equity calculated in Position Valuation Section
            # Used Margin: sum of (amount*price) all futures orders type limit
            used_margin = 0
            for order in client.futures_get_open_orders():
                if order['type'] == 'LIMIT' or order['type'] == 'MARKET':
                    used_margin += float(order['price']) * float(order['origQty'])

            used_margin = round(used_margin, 2)
            # ===================== Position Valuation ================
            opening_cost, current_valuation, futures_profit, futures_loss, accumulated_profit, today_profit_volume \
                = HomeModules.position_valuation(request, client, opening_cost, current_valuation, spot_profit, today_trade_volume)

            # ===================== Open Orders Spot ================
            open_orders_spot, spot_used_margin = HomeModules.open_orders_spot(request, client, spot_used_margin)

            # ==================== Deposits  ========================
            pending_balance, deposit_list = HomeModules.deposits(request, client)

            # ================= Withdrawals =========================
            withdrawals, pending_balance = HomeModules.withdrawls(request, client, pending_balance)

            futures_balance = HomeModules.futures_bal(request, client)

            free_margin = futures_balance
            futures_equity = futures_profit + futures_loss + futures_balance
            spot_equity = spot_profit + spot_loss + spot_balance
            equity = round(spot_equity + futures_equity, 2)
            loss = round(spot_loss + futures_loss, 2)
            profit = round(spot_profit + futures_profit, 2)
            # ratio of equity to used margin
            margin_level = 0
            if used_margin > equity:
                margin_level = equity / used_margin * 100
            elif used_margin < equity:
                margin_level = used_margin / equity * 100
            margin_level = round(margin_level, 2)

            price_btc = float(requests.get(url + "BTCUSDT").json()['price'])
            locked_balance = locked_balance_spot
            locked_balance = round(locked_balance, 2)
            available_balance = spot_balance + futures_balance
            available_balance = round(available_balance, 2)
            available_balance_btc = 1 / price_btc * available_balance
            available_balance_btc = round(available_balance_btc, 12)
            locked_btc = 1 / price_btc * locked_balance
            pending_btc = 1 / price_btc * pending_balance
            locked_btc = round(locked_btc, 12)
            pending_btc = round(pending_btc, 12)

            # ======================== Transfers ===========================
            transfer_list = HomeModules.transfers(request, client)

            # ======================= analytics graph ========================
            balances_dict, date_dict, all_time_high = HomeModules.analytics_graph(request, client, user, symbol_dict)

            # Convert USD to other currencies if user switches between currencies
            if currency != "USD":
                for key in balances_dict:
                    bal_list = balances_dict[key]
                    new_list = list()
                    for item in bal_list:
                        value = c.convert(item, 'USD', currency)
                        value = round(value, 2)
                        new_list.append(value)
                    balances_dict[key] = new_list
                spot_balance = c.convert(spot_balance, 'USD', currency)
                spot_balance = round(spot_balance, 2)
                for item in balance_list:
                    value = item[3]
                    new_value = c.convert(value, 'USD', currency)
                    new_value = round(new_value, 2)
                    item[3] = new_value

                if accumulated_profit > 0:
                    accumulated_profit = c.convert(accumulated_profit, 'USD', currency)
                    accumulated_profit = round(accumulated_profit, 2)
                if today_trade_volume > 0:
                    today_trade_volume = c.convert(today_trade_volume, 'USD', currency)
                    today_trade_volume = round(today_trade_volume, 2)

                all_time_high = c.convert(all_time_high, 'USD', currency)
                all_time_high = round(all_time_high, 2)

                futures_balance = c.convert(futures_balance, 'USD', currency)
                futures_balance = round(futures_balance, 2)

                equity = c.convert(equity, 'USD', currency)
                equity = round(equity, 2)

                used_margin = c.convert(used_margin, 'USD', currency)
                used_margin = round(used_margin, 2)

                free_margin = c.convert(free_margin, 'USD', currency)
                free_margin = round(free_margin, 2)

                opening_cost = c.convert(opening_cost, 'USD', currency)
                opening_cost = round(opening_cost, 2)

                current_valuation = c.convert(current_valuation, 'USD', currency)
                current_valuation = round(current_valuation, 2)

                profit = c.convert(profit, 'USD', currency)
                profit = round(profit, 2)

                loss = c.convert(loss, 'USD', currency)
                loss = round(loss, 2)

                fees = c.convert(fees, 'USD', currency)
                fees = round(fees, 2)

                available_balance = c.convert(available_balance, 'USD', currency)
                available_balance = round(available_balance, 2)

                pending_balance = c.convert(pending_balance, 'USD', currency)
                pending_balance = round(pending_balance, 2)

                locked_balance = c.convert(locked_balance, 'USD', currency)
                locked_balance = round(locked_balance, 2)

                # [sm, size, entry_price, mark_price, pnl, ROI]
                for item in spot_positions_l:
                    entry_price = c.convert(item[2], 'USD', currency)
                    mark_price = c.convert(item[3], 'USD', currency)
                    pnl = c.convert(item[4], 'USD', currency)
                    item[2] = round(entry_price, 2)
                    item[3] = round(mark_price, 2)
                    item[4] = round(pnl, 2)

            # set  btc_balance, btc_amount session vars
            request.session['btc_balance'] = round(available_balance + locked_balance, 2)
            btc_amount = available_balance_btc + locked_btc
            btc_amount = round(btc_amount, 7)
            request.session['btc_amount'] = btc_amount

            current_hour = datetime.datetime.now().hour
            current_minute = datetime.datetime.now().minute
            remaining_hours = remainingTime(current_hour, current_minute)
            if 0 < remaining_hours < 4:
                messages.success(request, _(f"Your Today's profit is {request.user.currency_symbol}{accumulated_profit}"))
            context = {
                'balances_dict': jsonpickle.encode(balances_dict),
                'currency_symbol': currency_symbol,
                'currency': currency,
                'label_list': jsonpickle.encode(label_list),
                'item_percentages': jsonpickle.encode(item_percentages),
                'balance_list': balance_list,
                'color_list': jsonpickle.encode(color_list),
                'equity': equity,
                'positionAmt': 0,
                'loss': loss,
                'profit': profit,
                'available_balance_btc': available_balance_btc,
                'locked_btc': locked_btc,
                'pending_btc': pending_btc,
                'spot_balance': spot_balance,
                'futures_balance': futures_balance,
                'available_balance': available_balance,
                'locked_balance': locked_balance,
                'pending_balance': pending_balance,
                'used_margin': used_margin,
                'free_margin': free_margin,
                'margin_level': margin_level,
                'opening_cost': opening_cost,
                'current_valuation': current_valuation,
                'deposit_list': deposit_list,
                'withdrawals': withdrawals,
                'transfer_list': transfer_list,
                'open_orders_spot': open_orders_spot,
                'fees': fees,
                'date_dict': jsonpickle.encode(date_dict),
                'all_time_high': all_time_high,
                'accumulated_profit': accumulated_profit,
                'today_trade_volume': today_trade_volume,
                'today_profit_volume': today_profit_volume,
                'spot_positions_l': spot_positions_l,
                'home_page': True,
            }
            return render(request, 'home/welcome.html', context)
        else:
            generic_context['no_keys'] = True
            messages.success(request, _("Please add the api keys for your binance account"))
            return render(request, 'home/welcome.html', generic_context)
    except BinanceAPIException as e:
        # print(e.status_code)
        print('error_code', e.code)
        print('error_msg', e.message)
        if e.code == -2015:
            generic_context['error_code'] = str(e.code)
            msg = _("Invalid api keys, IP or permissions for action.")
            messages.success(request, msg)
            return render(request, 'home/welcome.html', generic_context)
        if e.code == -1003:
            generic_context['error_code'] = str(e.code)
            return render(request, 'home/welcome.html', generic_context)
        messages.warning(request, e.message)
        return render(request, 'home/welcome.html', generic_context)


def generate_pdf(request):
    return HttpResponse('yes')


class account_confirm_email_custom(ConfirmEmailView):
    def post(self, *args, **kwargs):
        super(account_confirm_email_custom).post(self, *args, **kwargs)
        redirect_url = 'account_login'
        return redirect(redirect_url)


def pre_login_check(request):
    user = request.user
    print("USER======>", user)
    # confirm if ip, browser or location is same
    ip, near, browser = get_ip_and_location(request, get_browser=True)
    objs = AllLogin.objects.filter(user=request.user)
    different_login = False

    response = redirect('home:home')
    if objs:
        ip_current = ip.split(".")
        ip_current = ip_current[0] + "." + ip_current[1]
        objs_exist = objs.filter(ip_address__startswith=ip_current, near=near, browser=browser)
        if not objs_exist:
            auth_code = cache.get('auth_code')
            auth_code1 = request.session.get('auth_code')
            auth_code2 = request.COOKIES.get('auth_code')

            print('auth_code', auth_code, auth_code1, auth_code2)
            code = None
            if auth_code:
                code = auth_code
                cache.delete('auth_code')
            elif auth_code1:
                code = auth_code1
                del request.session['auth_code']
            elif auth_code2:
                code = auth_code2
                response.delete_cookie('auth_code')

            login_code = user.login_code
            if login_code and login_code != "" and login_code == code:
                pass
            else:
                different_login = True

    if different_login:
        subject = 'A New Device Tried To Login Your Account'
        code = generate_ref_code()
        user.login_code = code
        user.save()
        context = {
            'code': code,
            'location': near,
            'ip': ip,
            'browser': browser,
        }
        msg_html = render_to_string('account/email/confirm_account_login.html', context)
        send_mail(
            subject,
            msg_html,
            settings.EMAIL_HOST_USER,
            [request.user.email, ],
            html_message=msg_html,
        )
        logout(request)
        return redirect('confirm_login')

    # print facebook account extra data
    fb_extra_data = SocialAccount.objects.filter(provider='facebook', user=user)
    if fb_extra_data:
        fb_extra_data = fb_extra_data.first().extra_data
        print('fb_extra_data', fb_extra_data)
        fb_id = fb_extra_data['id']
        c_email = 'user_' + str(fb_id)
        if not user.email or user.email == "":
            user.email = c_email
            user.save()
    ref_user_id1 = cache.get('ref_user_id')
    ref_user_id2 = request.COOKIES.get('ref_user_id')
    ref_user_id = None
    if ref_user_id1:
        print('ref_user_id1', ref_user_id1)
        ref_user_id = ref_user_id1
    if ref_user_id2:
        print('ref_user_id2', ref_user_id2)
        ref_user_id = ref_user_id2
    if ref_user_id and not user.recommended_by:
        ref_user = User.objects.get(id=ref_user_id)
        ref_user.days_remaining += 3
        user.recommended_by = ref_user
        user.save()
        ref_user.save()
        user.days_remaining += 3
        user.save()
        messages.success(request, _('Congrats On getting 3 extra days for joining through the referral link.'))
        cache.delete('ref_user_id')
    firstname = request.user.first_name
    if not firstname:
        user = request.user
        social_account_id = SocialAccount.objects.filter(provider='linkedin_oauth2', user=user).first().id
        linkedin_app_id = SocialApp.objects.filter(provider='linkedin_oauth2').first().id
        token = SocialToken.objects.filter(app=linkedin_app_id, account=social_account_id).first().token
        headers = {
            'content-type': 'application/json',
            'Authorization': f"Bearer {token}",
        }
        url = "https://api.linkedin.com/v2/me"
        data = requests.get(url, headers=headers).json()
        lastname = data['localizedLastName']
        firstname = data['localizedFirstName']
        user.first_name = firstname
        user.last_name = lastname
        user.save()

    # crete alllogin object
    create_login_session(request)
    return response
