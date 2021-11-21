"""
Django settings for dashboard project.

Generated by 'django-admin startproject' using Django 3.1.4.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""
from pathlib import Path
import pytz
import os
# import django_heroku
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

# import dropbox  # remove this
# from easy_thumbnails.conf import Settings as thumbnail_settings
# import mimetypes
# mimetypes.add_type("application/javascript", ".js", True)


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'v589_%ir&upblwhrusem7c*(jhpf+y@gd(k+(j78f$+#3ke50h'

 
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG=True
ALLOWED_HOSTS = ['nftion-test2.herokuapp.com','127.0.0.1', '127.0.0.1:8000', "localhost"]

# Application definition
CRISPY_TEMPLATE_PACK = 'bootstrap4'
# CRISPY_ALLOWED_TEMPLATE_PACKS = ["gds"]
# CRISPY_TEMPLATE_PACK = "gds"
INSTALLED_APPS = [
    # 'djangocms_admin_style',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    # 'home.apps.HomeConfig',
    'members',
    'users',
    'allauth',
    'balances',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.linkedin_oauth2',
    'cms',
    'menus',
    'treebeard',
    'sekizai',
    'translation_manager',
    'rosetta',
    'autotranslate',
    'corsheaders',
    'django_user_agents',
    'cropperjs',
    'tinymce',
    'crispy_forms',
    'home'
    # 'crispy_forms_gds',
]

TINYMCE_DEFAULT_CONFIG = {
    'height': 360,
    'width': 1000,
    'cleanup_on_startup': True,
    'custom_undo_redo_levels': 20,
    'selector': 'textarea',
    'theme': 'modern',
    'plugins': '''
   textcolor save link image media preview codesample contextmenu
   table code lists fullscreen insertdatetime nonbreaking
   contextmenu directionality searchreplace wordcount visualblocks
   visualchars code fullscreen autolink lists charmap print hr
   anchor pagebreak
   ''',
    'toolbar1': '''
   fullscreen preview bold italic underline | fontselect,
   fontsizeselect | forecolor backcolor | alignleft alignright |
   aligncenter alignjustify | indent outdent | bullist numlist table |
   | link image media | codesample |
   ''',
    'toolbar2': '''
   visualblocks visualchars |
   charmap hr pagebreak nonbreaking anchor | code |
   ''',
    'contextmenu': 'formats | link image',
    'menubar': True,
    'statusbar': True,
}


# CRISPY_TEMPLATE_PACK = 'uni_form'



# Cache backend is optional, but recommended to speed up user agent parsing
# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
#         'LOCATION': 'localhost:8000',
#     }
# }

# Name of cache backend to cache user agents. If it not specified default
# cache alias will be used. Set to `None` to disable caching.
# USER_AGENTS_CACHE = 'default'


ROSETTA_LANGUAGE_GROUPS = True

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email', 'openid'],
        'AUTH_PARAMS': {'access_type': 'online'},
        'VERIFIED_EMAIL': True,
               },
    'facebook': {
        'METHOD': 'oauth2',
        # 'SDK_URL': '//connect.facebook.net/{locale}/sdk.js',
        'SCOPE': ['email', 'public_profile'],

        'INIT_PARAMS': {'cookie': True},
        'FIELDS': [
            'id',
            'email',
            'first_name',
            'last_name',
            'middle_name',
            'name',
            'name_format',
            'picture',
            'short_name'
        ],
        'VERIFIED_EMAIL': True,
    },
    'linkedin_oauth2': {
        'SCOPE': [
            # 'r_basicprofile',
            'r_liteprofile',
            'r_emailaddress',
            # 'r_fullprofile',
            # 'w_member_social',
        ],
        'PROFILE_FIELDS': [
            'id',
            'first-name',
            'last-name',
            'email-address',
            'picture-url',
            'public-profile-url',
        ],
        'VERIFIED_EMAIL': True,
    }
    # 'twitter': {}
}

AUTH_USER_MODEL = 'users.CustomUser'
# SOCIAL_AUTH_USER_MODEL = 'users.CustomUser'

ACCOUNT_FORMS = {
    'login': 'allauth.account.forms.LoginForm',
    # 'login': 'users.forms.MyCustomLoginForm',
    # 'signup': 'allauth.account.forms.SignupForm',
    'signup': 'users.forms.MyCustomSignupForm',
    'add_email': 'allauth.account.forms.AddEmailForm',
    'change_password': 'allauth.account.forms.ChangePasswordForm',
    'set_password': 'allauth.account.forms.SetPasswordForm',
    'reset_password': 'allauth.account.forms.ResetPasswordForm',
    'reset_password_from_key': 'allauth.account.forms.ResetPasswordKeyForm',
    'disconnect': 'allauth.socialaccount.forms.DisconnectForm',
}

# SOCIALACCOUNT_FORMS = {
    # 'disconnect': 'allauth.socialaccount.forms.DisconnectForm',
    # 'signup': 'allauth.socialaccount.forms.SignupForm',
    # 'signup': 'users.forms.CustomSignupForm',
# }

AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    "django.middleware.locale.LocaleMiddleware",
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'cms.middleware.user.CurrentUserMiddleware',
    'cms.middleware.page.CurrentPageMiddleware',
    'cms.middleware.toolbar.ToolbarMiddleware',
    'cms.middleware.language.LanguageCookieMiddleware',
    'users.middleware.TimezoneMiddleware',
    'django_user_agents.middleware.UserAgentMiddleware',
    'dashboard.middleware.CustomMiddleware',
]
X_FRAME_OPTIONS = 'ALLOWALL'  # SAMEORIGIN, ALLOWALL, DENY

CORS_ORIGIN_ALLOW_ALL = True  # If this is used then `CORS_ORIGIN_WHITELIST` will not have any effect

ROOT_URLCONF = 'dashboard.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.i18n',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'sekizai.context_processors.sekizai',
                'cms.context_processors.cms_settings',
                # 'users.context_processors.common_variables',
            ],
        },
    },
]

WSGI_APPLICATION = 'dashboard.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'dashboard',
#         'USER': 'postgres',
#         'PASSWORD': '123456',
#         'HOST': 'localhost',
#         'PORT': '5435',
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
# import dj_database_url
# db_from_env = dj_database_url.config(conn_max_age=600)
# DATABASES['default'].update(db_from_env)
# # Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/
# LANGUAGES = [
#     ('de', 'German'),
#     ('en', 'English'),
#     ('nl', 'Dutch'),
#     ('fr', 'French')
# ]

LANGUAGES = [
    ('en', _('English')),
    ('ru', _('Russian')),
    ('es', _('Spanish')),
    ('ja', _('Japanese')),
    ('hi', _('Hindi')),
    ('fr', _('French')),
    ('de', _('German')),
    ('sv', _('Swedish')),
    # ('zh-Hans', _('Chinese')),
]

LANGUAGE_CODE = 'en'  # 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('127.0.0.1', 6379), ],
        }
    }
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'
STATICFILES_LOCATION = 'static'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, "static/media_root")

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# Ensure SITE_ID is set sites app

SITE_ID = 1

# =============== Email Settings ===============

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_USE_TLS = True
EMAIL_PORT = 587
# EMAIL_USE_SSL = False

deploy=False
if deploy:
    EMAIL_HOST = 'smtppro.zoho.eu'
    EMAIL_HOST_USER = 'infiniqus2021@gmail.com'
    EMAIL_HOST_PASSWORD = 'Ramzan1996@'
    DEFAULT_FROM_EMAIL = 'help@nfticon.io'
else:
    EMAIL_HOST = "smtp.zoho.com"
    EMAIL_HOST_USER = "help@nfticon.io"
    EMAIL_HOST_PASSWORD = "Ramzan1996@"

# =============== Redirects ===============
LOGOUT_REDIRECT_URL = 'account_login'
LOGIN_URL = "account_login"
LOGIN_REDIRECT_URL = '/'


# =============== Custom allauth settings ===============
# Use email as the primary identifier
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'  # "mandatory", "optional", or "none"
#  If this is mandatory, social account verification will automatically be set to 'mandatory' as well

ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = 'account_login'
ACCOUNT_LOGOUT_REDIRECT_URL = 'account_login'  # account_login
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = False
ACCOUNT_USER_MODEL_USERNAME_FIELD = "username"
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3
ACCOUNT_AUTHENTICATION_METHOD = "email"     # Defaults to username_email
ACCOUNT_UNIQUE_EMAIL = True                 # Defaults to True
ACCOUNT_EMAIL_REQUIRED = True               # Defaults to False
ACCOUNT_USERNAME_REQUIRED = False           # Defaults to True
ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 20
# ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_USERNAME_BLACKLIST = ['admin','gay','fuck','shit','bitch','faggot','superuser', 'user']
SOCIALACCOUNT_QUERY_EMAIL = ACCOUNT_EMAIL_REQUIRED
SOCIALACCOUNT_AUTOMATICALLY_CONNECT = True
SOCIALACCOUNT_EMAIL_VERIFICATION = "none"
SOCIALACCOUNT_EMAIL_REQUIRED = False
SOCIALACCOUNT_AUTO_SIGNUP = True
# SOCIALACCOUNT_UNIQUE_EMAIL = False
 
# SOCIALACCOUNT_STORE_TOKENS = True
# SOCIALACCOUNT_EMAIL_REQUIRED = False

# Activate Django-Heroku.
# django_heroku.settings(locals())

SOCIALACCOUNT_ADAPTER = "dashboard.adapter.MySocialAccountAdapter" 
# ACCOUNT_SESSION_REMEMBER = True


# Contains the path list where Django should look into for django.po files for all supported languages
LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)
# dbx = dropbox.Dropbox('A5nUCB4RrlwAAAAAAAAAASnX01n9CiopgtaNbAq78ZnRj1oV_ntXpx3FqSfz8RAF')


# TRANSLATIONS_BASE_DIR = os.path.join(BASE_DIR, 'locale')

# AUTOTRANSLATE_TRANSLATOR_SERVICE = 'autotranslate.services.GoogleAPITranslatorService'
# GOOGLE_TRANSLATE_KEY = 'AIzaSyCICMVxFtpvN8y45ACd3eJROhe7TY6Ea-M'

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',  # this one
    'django.core.context_processors.request',
    'django.core.context_processors.static',
    'django.contrib.messages.context_processors.messages',
)

# CACHE_BACKEND = 'http://localhost:8000/'
# CACHE_BACKEND = 'locmem:///'

STRIPE_PUBLIC_KEY = "pk_test_51Hkp4ZJDNjt0xwAjNfOiET06tUPxhPuMy6RU8PDX2q7RfdIk99yAX58stcpKjUOh2CZrce2CnJyV3raJ8Bm6fwwn004Dghtkq4"
STRIPE_SECRET_KEY = "sk_test_51Hkp4ZJDNjt0xwAjpoDiZd1M18TPPovP3ecLcZFmOMOeLtlHsOvyz4DdUpiKVfbEoCVvlUeQSG96bfW0GzqummQa0000fnoRpC"

# DEFAULT_FILE_STORAGE = 'storages.backends.dropbox.DropBoxStorage'
# DROPBOX_OAUTH2_TOKEN = "A5nUCB4RrlwAAAAAAAAAASnX01n9CiopgtaNbAq78ZnRj1oV_ntXpx3FqSfz8RAF"
# DROPBOX_WRITE_MODE = 'overwrite'


