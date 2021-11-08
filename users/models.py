import datetime
from django.contrib.auth.base_user import BaseUserManager
# from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _
from django.dispatch import receiver
from allauth.account.models import EmailAddress
from allauth.account.signals import email_confirmed
from home.utils import generate_ref_code
from django.utils import timezone
from django.urls import reverse
# from image_cropping import ImageRatioField
# from django.contrib.auth import get_user_model
# User = get_user_model()

from django.conf import settings
User = settings.AUTH_USER_MODEL


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """
    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    username = models.CharField(max_length=100, unique=True,null=False)
    email = models.EmailField('email', unique=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    user_description = models.CharField(max_length=500, null=True, blank=True)
    nft_profile_link = models.CharField(max_length=100, null=True, blank=True)
    behance_profile_link = models.CharField(max_length=100, null=True, blank=True)
    instagram_profile_link = models.CharField(max_length=100, null=True, blank=True)
    twitter_profile_link = models.CharField(max_length=100, null=True, blank=True)
    facebook_profile_link = models.CharField(max_length=100, null=True, blank=True)
    telegram_profile_link = models.CharField(max_length=100, null=True, blank=True)
    number_of_user_subscribers = models.CharField(max_length=100, null=True, blank=True)
    user_online_status = models.CharField(max_length=100, null=True, blank=True)
    image = models.ImageField(upload_to='users', null=True, blank=True)
    time_zone = models.CharField(max_length=200, default='UTC')
    default_currency = models.CharField(max_length=10, default='USD')
    currency_symbol = models.CharField(max_length=10, default='$')
    terms_of_use = models.BooleanField(default=True)
    privacy_policy = models.BooleanField(default=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    recommended_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='ref_by')
    # days_remaining = models.PositiveIntegerField(unique_for_date=True, default=0)
    stripe_id = models.CharField(max_length=200, null=True, blank=True)
    login_code = models.CharField(max_length=100, null=True, blank=True)
    payment_method = models.CharField(max_length=400, null=True, blank=True)
    subscribed = models.BooleanField(default=False)
    subscription_msg = models.TextField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    objects = CustomUserManager()

    def add_email_address(self, request, new_email):
        # Add a new email address for the user, and send email confirmation.
        # Old email will remain the primary until the new one is confirmed.
        return EmailAddress.objects.add_email(request, request.user, new_email, confirm=True)

    def save(self, *args, **kwargs):
        if not self.code or self.code == "":
            code = generate_ref_code()
            self.code = code
        super().save(*args, **kwargs)

    def get_remaining_days(self):
        date_joined = self.date_joined
        now = datetime.datetime.now(timezone.utc)
        delta = now - date_joined
        days_left = 30 - int(delta.days)
        if days_left < 0:
            days_left = 0
        return days_left

    def __str__(self):
        return self.email
    def get_absolute_url(self):
        return reverse('home:home')


@receiver(email_confirmed)
def update_user_email(sender, request, email_address, **kwargs):
    # Once the email address is confirmed, make new email_address primary.
    # This also sets user.email to the new email address.
    # email_address is an instance of allauth.account.models.EmailAddress
    email_address.set_as_primary()
    # Get rid of old email addresses
    stale_addresses = EmailAddress.objects.filter(
        user=email_address.user).exclude(primary=True).delete()


class Privacy_Policy(models.Model):
    privacy_content = models.TextField(null=True, blank=True)

    def __str__(self):
        return str('privacy policy')


class Cookies_Policy(models.Model):
    cookies_content = models.TextField(null=True, blank=True)

    def __str__(self):
        return 'Cookies'


class API_KEY(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    public_key = models.CharField(max_length=500, unique=True)
    secret_key = models.CharField(max_length=500, unique=True)
    exchange = models.CharField(max_length=500)

    def __str__(self):
        return self.user.first_name + " " + self.exchange + " Keys"


class AllLogin(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    browser = models.CharField(max_length=500)
    ip_address = models.CharField(max_length=500)
    near = models.CharField(max_length=500)
    signed_in = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} signed in near {self.near}"


class UserActivity(models.Model):
    action = models.TextField(null=True, blank=True)
    source = models.CharField(max_length=500, null=True, blank=True)
    ip_address = models.CharField(max_length=500)
    location = models.CharField(max_length=500)
    when = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.action[:30] + '...'


class AuthCode(models.Model):
    code = models.CharField(max_length=200)

    def save(self, *args, **kwargs):
        if not self.code or self.code == "":
            code = generate_ref_code()
            self.code = code
        super().save(*args, **kwargs)

    def __str__(self):
        return self.code
