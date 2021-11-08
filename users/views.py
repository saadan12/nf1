from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.views.generic import DetailView,CreateView
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.urls import reverse_lazy
from .forms import ProfilePageForm,EditEveraveProfile,EditEveraveProfileSettings
from .models import CustomUser
from home.models import Post

from django.contrib.auth import get_user_model
User = get_user_model()

class ShowProfilePageView(DetailView):
    model = CustomUser
    template_name = 'registration/user_profile.html'

    def get_context_data(self, *args, **kwargs):
        users = CustomUser.objects.all()
        context = super(ShowProfilePageView, self).get_context_data(*args, **kwargs)

        page_user = get_object_or_404(CustomUser, username=self.kwargs['username'])

        logged_in_user_posts = Post.objects.filter(author=page_user)
        logged_in_user_liked_posts = User.objects.prefetch_related('blog_post').get(pk=page_user.id).blog_post.all()

        context['logged_in_user_posts'] = logged_in_user_posts
        context['logged_in_user_liked_posts'] = logged_in_user_liked_posts
        context['page_user'] = page_user
        return context

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        # print(self.kwargs)
        # try_
        name = self.kwargs['username'] or self.request.GET.get('username') or None
        # print(name)
        queryset = queryset.filter(username=name)
        obj = queryset.get()
        return obj

class EditProfilePageView(generic.UpdateView):
    model = CustomUser
    form_class = EditEveraveProfile
    template_name = 'registration/edit_everave_profile.html'
    # success_url = reverse_lazy('home:home')
    # fields = ['first_name', 'last_name','username','user_description', 'image', 'email', 'nft_profile_link', 'behance_profile_link', 'instagram_profile_link', 'twitter_profile_link', 'facebook_profile_link', 'telegram_profile_link', 'twitter_profile_link']
    def get_context_data(self, *args, **kwargs):
        users = CustomUser.objects.all()
        context = super(EditProfilePageView, self).get_context_data(*args, **kwargs)
        page_user = get_object_or_404(CustomUser, username=self.kwargs['username'])
        context['page_user'] = page_user
        return context



    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        # print(self.kwargs)
        # try_
        name = self.kwargs['username'] or self.request.GET.get('username') or None
        # print(name)
        queryset = queryset.filter(username=name)
        obj = queryset.get()
        return obj

class EditProfileSettingsView(generic.UpdateView):
    model = CustomUser
    form_class = EditEveraveProfileSettings
    template_name = 'registration/edit_everave_profile_settings.html'
    # success_url = reverse_lazy('home:home')
    # fields = ['first_name', 'last_name','username','user_description', 'image', 'email', 'nft_profile_link', 'behance_profile_link', 'instagram_profile_link', 'twitter_profile_link', 'facebook_profile_link', 'telegram_profile_link', 'twitter_profile_link']
    def get_context_data(self, *args, **kwargs):
        users = CustomUser.objects.all()
        context = super(EditProfileSettingsView, self).get_context_data(*args, **kwargs)
        page_user = get_object_or_404(CustomUser, username=self.kwargs['username'])
        context['page_user'] = page_user
        return context



    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        # print(self.kwargs)
        # try_
        name = self.kwargs['username'] or self.request.GET.get('username') or None
        # print(name)
        queryset = queryset.filter(username=name)
        obj = queryset.get()
        return obj
