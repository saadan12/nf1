from django.db import models

from django.conf import settings
from cropperjs.models import CropperImageField

User = settings.AUTH_USER_MODEL


# coin , date, balance
class Coin(models.Model):
    name = models.CharField(max_length=100)
    image = CropperImageField(upload_to='icons', null=True, blank=True)

    def __str__(self):
        return self.name


class CoinBalance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    coin = models.ForeignKey(Coin, on_delete=models.CASCADE)
    date = models.CharField(max_length=200)
    balance = models.CharField(max_length=100)

    def __str__(self):
        return str(self.coin.name) + ': ' + str(self.balance) + ', ' + str(self.date)
