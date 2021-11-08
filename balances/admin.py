from django.contrib import admin
from .models import Coin, CoinBalance

# Register your models here.
admin.site.register(Coin)
admin.site.register(CoinBalance)
