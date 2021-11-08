from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import datetime, date
from django.conf import settings



class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)
    bio = models.TextField()
    bio1 = models.TextField()
    profile_pic = models.ImageField(upload_to='images/profile', null=True, blank=True)

    behance_profile_url = models.CharField(max_length=120, null=True, blank=True)
    twitter_profile_url = models.CharField(max_length=100, null=True, blank=True)
    facebook_profile_url = models.CharField(max_length=100, null=True, blank=True)
    linkedin_profile_url = models.CharField(max_length=100, null=True, blank=True)
    telegram_profile_url = models.CharField(max_length=100, null=True, blank=True)
    def __str__(self):
        return str(self.user)

    def get_absolute_url(self):
        return reverse('home')


class OpenSeaAsset(models.Model):
    contract_address = models.CharField(max_length=300,null=True)
    asset_name = models.CharField(max_length=120,null=True)
    asset_slug = models.SlugField(null=True)
    asset_token_id = models.CharField(max_length=300,null=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='opensea_post')
    def save(self, *args, **kwargs):
        if not self.asset_slug:
            self.asset_slug = slugify(self.asset_name)
        return super().save(*args, **kwargs)
    def total_likes(self):
        return self.likes.count()
    def __str__(self):
        return self.asset_name + ' | OpenSea'
    def get_absolute_url(self):
        return reverse('home:home')



class Category(models.Model):
    name = models.CharField(max_length=245)
    def __str__(self):
        return self.name

    def get_absolute_url(self):
        # return reverse('article_detail', args=(str(self.id)))
        return reverse('home')


class Post(models.Model):
    asset_image = models.ImageField(upload_to='images/', null=True, blank=True)
    asset_name = models.CharField(max_length=120)
    asset_title_tag = models.CharField(max_length=255)
    asset_description = models.CharField(max_length=300)
    asset_slug = models.SlugField(null=True)
    asset_price = models.IntegerField()
    category = models.CharField(max_length=255, default='coding')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post_date = models.DateField(auto_now_add=True)
    owner = models.CharField(null=True, blank=True,max_length=100)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='blog_post')

    def save(self, *args, **kwargs):
        if not self.asset_slug:
            self.asset_slug = slugify(self.asset_name)
        return super().save(*args, **kwargs)

    def author_data(self):
        return self.author.id

    def total_likes(self):
        return self.likes.count()

    def __str__(self):
        return self.asset_name + ' | ' + str(self.author)

    def get_absolute_url(self):
        # return reverse('article_detail', args=(str(self.id)))
        return reverse('home:home')
