from allauth.account.forms import SignupForm, LoginForm
from django import forms
from allauth.account.adapter import get_adapter
from django.shortcuts import render, redirect
from allauth.socialaccount.forms import SignupForm as SocialSignupForm
from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from home.utils import persist_session_vars
from .models import CustomUser
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Fieldset, ButtonHolder, Submit, Layout,MultiField,Div,Row, Column,HTML,Field
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit,Layout,HTML,Div,Field,Button
from django.urls import reverse_lazy

User = get_user_model()


class EditEveraveProfile(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name','username','user_description', 'image', 'email', 'nft_profile_link', 'behance_profile_link', 'instagram_profile_link', 'twitter_profile_link', 'facebook_profile_link', 'telegram_profile_link')
        labels = {
            "first_name": "First name",
            "last_name":"Last name",
            "username":"Username",
            "user_description":"Description",
            "email":"Email",
            "nft_profile_link":"Link",
            "behance_profile_link":"Behance",
            "instagram_profile_link":"Instagram",
            "twitter_profile_link":"Twitter",
            "facebook_profile_link":"Facebook",
            "telegram_profile_link":"Telegram",

        }
        widgets = {
            'first_name':forms.TextInput(attrs={'class':'sign__input',"label": "dasdasdsdasd",'placeholder':"e. g. 'Crypto Heart'"}),
            'last_name':forms.TextInput(attrs={'class':'', 'id':'description','placeholder':"e. g. 'Last'"}),
            'username':forms.TextInput(attrs={'class': 'sign__input','placeholder': 'user12345'}),
            'user_description':forms.Textarea(attrs={'class':''}),
            'email':forms.TextInput(attrs={'class':'sign__input', 'placeholder': 'email@email.com', 'value':''}),
            'nft_profile_link':forms.TextInput(attrs={'class':'sign__input', 'placeholder': '', 'value':'', 'type':''}),
            'behance_profile_link':forms.TextInput(attrs={'class':'sign__input'}),
            'instagram_profile_link':forms.TextInput(attrs={'class':'sign__input', 'placeholder': '', 'value':'', 'type':''}),
            'twitter_profile_link':forms.TextInput(attrs={'class':'sign__input', 'placeholder': '', 'value':'', 'type':''}),
            'facebook_profile_link':forms.TextInput(attrs={'class':'sign__input', 'placeholder': '', 'value':'', 'type':''}),
            'telegram_profile_link':forms.TextInput(attrs={'class':'sign__input', 'placeholder': '', 'value':'', 'type':''}),
            }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse_lazy('home:home')
        self.helper.form_method = 'POST'
        self.helper.form_tag = False
        self.helper.layout = Layout(
        Div(
            HTML('<h4 class="sign__title">Profile details</h4>'), css_class="col-12"),
        Div(
            HTML('<h4 class="sign__title">Upload file</h4>'), css_class="col-12"),
        Div(
            Div(Field('image', css_id="sign__file-upload", css_class="sign__file-upload"),
                css_class="sign__file"), css_class="col-12"),
        Div(
            Div(Field('username', css_id="username", css_class="sign__input"),
                css_class="sign__group"), css_class="col-12"),
        Div(
            Div(Field('email', css_id="email", css_class="sign__input"),
                css_class="sign__group"), css_class="col-12"),
        Div(
            Div(Field('first_name', css_id="firstname", css_class="sign__input"),
                css_class="sign__group"), css_class="col-12"),
        Div(
            Div(Field('last_name', css_id="lastname", css_class="sign__input"),
                css_class="sign__group"), css_class="col-12"),
        Div(
            Div(Field('user_description', css_class="sign__textarea"),
                css_class="sign__group"), css_class="col-12"),
        Div(
            Div(Field('nft_profile_link', css_id="nft_profile_link", css_class="sign__input"),
                css_class="sign__group"), css_class="col-12"),
        Div(
            Div(Field('behance_profile_link', css_id="behance_profile_link", css_class="sign__input"),
                css_class="sign__group"), css_class="col-12"),
        Div(
            Div(Field('instagram_profile_link', css_id="instagram_profile_link", css_class="sign__input"),
                css_class="sign__group"), css_class="col-12"),
        Div(
            Div(Field('twitter_profile_link', css_id="twitter_profile_link", css_class="sign__input"),
                css_class="sign__group"), css_class="col-12"),
        Div(
            Div(Field('facebook_profile_link', css_id="facebook_profile_link", css_class="sign__input"),
                css_class="sign__group"), css_class="col-12"),
        Div(
            Div(Field('telegram_profile_link', css_id="telegram_profile_link", css_class="sign__input"),
                css_class="sign__group"), css_class="col-12")
        )
    

class EditEveraveProfileSettings(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('privacy_policy',)
        labels = {
            "privacy_policy": "Privacy policy",

        }
        widgets = {
            'privacy_policy':forms.TextInput(attrs={'class':'sign__input',"label": "dasdasdsdasd",'placeholder':"e. g. 'Crypto Heart'"}),
            }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse_lazy('home:home')
        self.helper.form_method = 'POST'
        self.helper.form_tag = False
        self.helper.layout = Layout(
        Div(
            HTML('<h4 class="sign__title">Profile settings</h4>'), css_class="col-12"),
        Div(
            Div(Field('privacy_policy', css_id="username", css_class="sign__input"),
                css_class="sign__group"), css_class="col-12"),
        )





class ProfilePageForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('user_description', 'image', 'behance_profile_link', 'twitter_profile_link', 'facebook_profile_link', 'instagram_profile_link', 'telegram_profile_link')
        widgets = {
            'user_description':forms.Textarea(attrs={'class':'form-control','placeholder':'Your biography'}),
            # 'profile_pic':forms.Textarea(attrs={'class':'form-control'}),
            'behance_profile_link':forms.TextInput(attrs={'class': 'form-control'}),
            'twitter_profile_link':forms.TextInput(attrs={'class':'form-control'}),
            'facebook_profile_link':forms.TextInput(attrs={'class':'form-control'}),
            'instagram_profile_link':forms.TextInput(attrs={'class':'form-control'}),
            'telegram_profile_link':forms.TextInput(attrs={'class':'form-control'}),
            }







# class MyCustomSignupForm(SignupForm):
#     def __init__(self, *args, **kwargs):
#         super(MyCustomSignupForm, self).__init__(*args, **kwargs)
#         self.fields['first_name'] = forms.CharField(required=False)
#
#     def save(self, request):
#         first_name = self.cleaned_data.pop('first_name')
#         ...
#         user = super(MyCustomSignupForm, self).save(request)


class MyCustomSignupForm(SignupForm):
    username = forms.CharField(max_length=100)

    def clean(self):
        super(SignupForm, self).clean()
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password1")
        email = self.cleaned_data.get("email")
        if email is None:
            return redirect('/')
        if password:
            password = password
        if username:
            return redirect('/')
        return self.cleaned_data


class CustomSignupForm(SocialSignupForm):
    def __init__(self, *args, **kwargs):
        super(CustomSignupForm, self).__init__(*args, **kwargs)

    @method_decorator(persist_session_vars(['ref_user_id']))
    def save(self, request):
        # print('session variable - SocialSignupForm', request.session.get('ref_user_id'))
        user = super(CustomSignupForm, self).save(request)
        ref_user_id = request.session.get('ref_user_id')
        # print('user', user)
        if ref_user_id:
            ref_user = User.objects.get(id=ref_user_id)
            print('ref_user', ref_user)
            user.recommended_by = ref_user
            ref_user.days_remaining += 3
            ref_user.save()
            # del request.session['ref_user_id']
        user.save()
        return user


class ProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.fields['image'].widget.attrs = {'class': 'form-file-input', 'id': 'customFile'}

    class Meta:
        model = CustomUser
        # The fields that will be visible in the form
        fields = ['image', ]
