from django.urls import path, include
from . import views
# from .views import redirect_view
from home.views import (
    biance_test, pre_login_check, lib_file, lib_file2, generate_pdf,
    update_profile, change_email, update_preferences,
    generate_csv)
from dashboard.views import ProfileView
from allauth.account.views import LoginView, SignupView
from django.views.generic import TemplateView
from .views import HomeView, LikeView, ArticleDetailView, AddPostView, UpdatePostView, DeletePostView, AddCategoryView, CategoryView, CategoryListView,OriginAddView,ArticleDetailViewOS

limit_list = list()
for i in range(1, 11):
    limit_list.append(i*100)

context = {
            'position_list': [],
            'btc_amount': 22,
            'btc_balance': 11,
            'currency': 'USD',
            'currency_symbol': '$',
            'tab': 'trade',
            'limit_list': limit_list,
          }

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('signin/', LoginView.as_view(), name='account_login'),
    path('join/<str:ref_code>/', views.home, name='home'),
    path('login-check', pre_login_check, name='pre_login_check'),
    # path('test', biance_test, name='test'),
    path('blank/', ProfileView.Blank, name='blank'),
    path('intro/', ProfileView.Intro, name='intro'),
    path('lock/', ProfileView.Lock, name='lock'),
    path('otp-1/', ProfileView.Otp1, name='otp-1'),
    path('otp-2/', ProfileView.Otp2, name='otp-2'),
    path('price/', ProfileView.Price, name='price'),
    path('reset/', ProfileView.Reset, name='reset'),
    path('signup/', ProfileView.SignUp, name='signup'),
    # path('wallet/', ProfileView.Wallet, name='wallet'),
    # path('trade/', ProfileView.Trade, name='trade'),
    # path('signin/', ProfileView.SignIn, name='account_login'),
    # path('price-details/', ProfileView.PriceDetails, name='price-details'),
    path('verify-email/', ProfileView.VerifyEmail, name='verify-email'),
    # path('chart/', TemplateView.as_view(template_name='charting-library/chart.html'), kwargs=context, name='chart'),
    path('change-email/', change_email, name='change_email'),
    path('save-preferences', update_preferences, name='update_preferences'),
    # path('home/', HomeView.as_view(), name="home_alt"),
    path('asset/<slug:asset_slug>/', ArticleDetailView.as_view(), name='article_detail'),
    # path('asset/<slug:asset_slug>/', ArticleDetailView.as_view(), name='article_detail'),
    path('add-asset/', AddPostView.as_view(), name='add-asset'),
    path('add-orig-asset/', OriginAddView.as_view(), name='add_orig_asset'),
    path('add_category/', AddCategoryView.as_view(), name='add_category'),
    path('article/edit/<slug:asset_slug>/', UpdatePostView.as_view(), name='update_post'),
    path('article/<slug:asset_slug>/remove', DeletePostView.as_view(), name='delete_post'),
    path('category/<str:cats>/', CategoryView, name='category'),
    path('category-list/', CategoryListView, name='category-list'),
    path('like/<slug:asset_slug>/', LikeView, name='like_post'),
    path('asset/os/<str:asset_token_id>/<str:contract_address>', ArticleDetailViewOS.as_view(),name='article_detail_os')
    # path('redirect/', redirect_view, name="books-home"),
    # path('books/', IndexView.as_view(), name='ex2'),
    # path('add/', AddBookView.as_view(), name='add'),
    # path('g/<str:genre>', GenreView.as_view(), name='genre'),
    # path('<slug:slug>/', BookDetailView.as_view(), name='book-detail'),
    # path('<slug:slug>/edit', BookEditView.as_view(), name='edit-detail'),
]

handler404 = 'home.views.custom_page_not_found_view'
handler500 = 'home.views.custom_error_view'
handler403 = 'home.views.custom_permission_denied_view'
handler400 = 'home.views.custom_bad_request_view'
    # path('export-data', generate_csv, name='generate_csv'),
    # path('export-pdf', generate_pdf, name='generate_pdf'),
    # path('charting_library_clonned_data/charting_library/<str:filename>', lib_file),
    # path('charting_library_clonned_data/charting_library/bundles/<str:filename>', lib_file2),
# ]
