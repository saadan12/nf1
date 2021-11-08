from django import forms
from .models import Post, Category
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Fieldset, ButtonHolder, Submit, Layout,MultiField,Div,Row, Column,HTML,Field
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit,Layout,HTML,Div,Field,Button
# import request
# from crispy_forms.layout import ButtonHolder
from django.urls import reverse_lazy


# from crispy_forms.layout import Field

class CustomCheckbox(Field):
    template = 'alt_partials/add_post.html'

choices = Category.objects.all().values_list('name','name')
choices_list=[]
for item in choices:
    choices_list.append(item)


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('asset_image', 'asset_name', 'asset_description', 'asset_price', 'category', 'author','owner')

        # fields='__all__'
        widgets = {
            'asset_name':forms.TextInput(attrs={'class':'sign__input','id':'itemname'}),
            'asset_description':forms.Textarea(attrs={'class':'sign__textarea', 'id':'description','placeholder':"e. g. 'After purchasing you will able to recived...'"}),
            'asset_price':forms.TextInput(attrs={'class': 'sign__input'}),
            'title_tag':forms.TextInput(attrs={'class':'form-control'}),
            'author':forms.TextInput(attrs={'class':'form-control', 'placeholder': '', 'value':'', 'id':'elder', 'type':'hidden'}),
            'owner':forms.TextInput(attrs={'class':'form-control', 'placeholder': '', 'value':'', 'type':'hidden'}),
            'category':forms.Select(choices=choices_list, attrs={'class':'sign__label'}),
            }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'sign__form sign__form--create'
        # self.helper.form_enctype = 'enctype sign__form--create'
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.layout = Layout(

            Div(
                Field('asset_image', css_id="sign__file-upload", css_class="sign__file-upload"),
                css_class="sign__file"),
            Div(
                Field('asset_name', css_class="sign__input"),
                css_class="sign__group"),
            Div(
                Field('asset_description', css_class="sign__textarea"),
                css_class="sign__group"),
            Div(
                Field('asset_price', css_class="sign__input"),
                css_class="sign__group"),
            Div(
                Field('category', css_class="sign__select"),
                css_class="sign__group"),


            # Button('button', 'Create item', css_class='sign__btn')

        )

class FileUploadForm(forms.ModelForm):

    # file = forms.FileField(label="e. g. Image, Audio, Video",
    #     help_text="Select the CSV file to upload.",
    #     error_messages={
    #         "required": "Choose the CSV file you exported from the spreadsheet"
    #     },
    # )
    class Meta:
        model = Post
        fields = ('asset_image', 'asset_name', 'asset_description', 'asset_price', 'category', 'author','owner')
        labels = {
            "asset_name": "Asset name",
            "asset_description":"Description",
            "asset_price":"Asset price",
            "category":"Categories"

        }
        widgets = {
            'asset_name':forms.TextInput(attrs={'class':'sign__label',"label": "dasdasdsdasd",'placeholder':"e. g. 'Crypto Heart'"}),
            'asset_description':forms.Textarea(attrs={'class':'sign__textarea', 'id':'description','placeholder':"e. g. 'After purchasing you will able to recived...'"}),
            'asset_price':forms.TextInput(attrs={'class': 'sign__input'}),
            'title_tag':forms.TextInput(attrs={'class':'form-control'}),
            'author':forms.TextInput(attrs={'class':'form-control', 'placeholder': '', 'value':'', 'id':'elder', 'type':'hidden'}),
            'owner':forms.TextInput(attrs={'class':'form-control', 'placeholder': '', 'value':'', 'type':'hidden'}),
            'category':forms.Select(choices=choices_list, attrs={'class':'sign__label'}),
            }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse_lazy('add_asset')
        self.helper.form_method = 'POST'
        self.helper.form_tag = False
        self.helper.layout = Layout(
        Div(
            HTML('<h4 class="sign__title">Upload file</h4>'), css_class="col-12"),
        Div(
            Div(Field('asset_image', css_id="sign__file-upload", css_class="sign__file-upload"),
                css_class="sign__file"), css_class="col-12"),
        Div(
            HTML('<h4 class="sign__title">Asset details</h4>'), css_class="col-12"),
        Div(
            Div(Field('asset_name', css_class="sign__input"),
            css_class="sign__group"), css_class="col-12"),
        Div(
            Div(Field('asset_description', css_class="sign__textarea"),
            css_class="sign__group"), css_class="col-12"),
        Div(
            Div(Field('asset_price', css_class="sign__input"),
            css_class="sign__group"), css_class="col-12"),
        Div(
            Div(Field('category', css_class="sign__select"),
            css_class="sign__group"),css_class="col-12 col-md-4"),
        Div(
            Field('author', css_class="sign__select"),
            css_class="sign__group"),
        Div(
            Field('owner', css_class="sign__select"),
            css_class="sign__group"),


        # ButtonHolder(
        #     Submit('submit', 'Create', css_class='sign__btn'),
        #     css_class="col-12 col-xl-3")
        )
        # Fieldset(
        #     '',
        #     HTML('<h4>Tell us more about yourself</h4>'),
        #     Field('resume'),
        # )








    def valid_layout(self):
        file = self.cleaned_data["file"]
        self.helper.layout = Layout(
            HTML.h2("You uploaded..."),
            HTML.p("File: %s" % file),
            HTML(
                '<a class="govuk-button" href="%s">Continue</a>'
                % reverse("home:home", kwargs={"class": "sign__file-upload"})
            ),
        )


class OriginAddAssetForm(forms.ModelForm):

    # file = forms.FileField(label="e. g. Image, Audio, Video",
    #     help_text="Select the CSV file to upload.",
    #     error_messages={
    #         "required": "Choose the CSV file you exported from the spreadsheet"
    #     },
    # )
    def clean(self):
        super(OriginAddAssetForm, self).clean()
        asset_image=self.cleaned_data.get("asset_image")
        asset_name = self.cleaned_data.get("asset_name")
        asset_description = self.cleaned_data.get("asset_description")
        asset_price = self.cleaned_data.get("asset_price")
        asset_to_post = Post.objects.get_or_create(asset_image=asset_image,
        asset_name=asset_name,
        asset_description=asset_description,
        asset_price=asset_price,author=request.user)
        # asset_description = self.cleaned_data.get("asset_description")
        # email = self.cleaned_data.get("email")
        if email is None:
            return redirect('/')
        if password:
            password = password
        if username:
            return redirect('/')
        return self.cleaned_data

    class Meta:
        model = Post
        fields = ('asset_image', 'asset_name', 'asset_description', 'asset_price', 'category', 'author','owner')
        widgets = {
            'asset_name':forms.TextInput(attrs={'class':'sign__input','id':'itemname'}),
            'asset_description':forms.Textarea(attrs={'class':'sign__textarea', 'id':'description','placeholder':"e. g. 'After purchasing you will able to recived...'"}),
            'asset_price':forms.TextInput(attrs={'class': 'sign__input'}),
            'title_tag':forms.TextInput(attrs={'class':'form-control'}),
            'author':forms.TextInput(attrs={'class':'form-control', 'placeholder': '', 'value':'', 'id':'elder', 'type':'hidden'}),
            'owner':forms.TextInput(attrs={'class':'form-control', 'placeholder': '', 'value':'', 'type':'hidden'}),
            'category':forms.Select(choices=choices_list, attrs={'class':'sign__label'}),
            }

class EditForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('asset_image', 'asset_name', 'asset_description', 'asset_price', 'category', 'author','owner')

        widgets = {
            'asset_name':forms.TextInput(attrs={'class':'form-control','placeholder':'This is title placeholder stuff'}),
            'asset_description':forms.Textarea(attrs={'class':'form-control'}),
            'asset_price':forms.TextInput(attrs={'class': 'form-control'}),
            'title_tag':forms.TextInput(attrs={'class':'form-control'}),
            'author':forms.TextInput(attrs={'class':'form-control', 'placeholder': '', 'value':'', 'id':'elder', 'type':'hidden'}),
            'owner':forms.TextInput(attrs={'class':'form-control', 'placeholder': '', 'value':'', 'id':'', 'type':'hidden'}),
            'category':forms.Select(choices=choices_list, attrs={'class':'form-control'}),
            }
