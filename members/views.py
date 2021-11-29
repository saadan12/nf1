from django.shortcuts import render, redirect
from django.views import generic
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.contrib.auth import logout
import stripe
from django.conf import settings
from django.http import JsonResponse
from django.views import View
from home.models import Post  
 
stripe.api_key = settings.STRIPE_SECRET_KEY


class CreateCheckoutSessionView(View):
    
    def post(self, request, *args, **kwargs):
        post_id = self.kwargs["pk"]
        post = Post.objects.get(id=post_id)
        YOUR_DOMAIN = "http://nftion-test2.herokuapp.com"
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': post.asset_price ,
                        'product_data': {
                            'name': "Test Payment"
                        },
                    },
                    'quantity': 1,
                },
            ], 
            mode='payment',
            success_url=YOUR_DOMAIN + '/members/success/',
            cancel_url=YOUR_DOMAIN + '/members/cancel/',
        )
         
        return redirect(checkout_session.url, code=303)

def confirm_payment(request):
    return render(request, 'success.html')

def cancel_payment(request):
    return render(request, 'cancel.html')


class UserRegisterView(generic.CreateView):
    form_class = UserCreationForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('login')


def logout_view(request):
    logout(request)
    # Redirect to a success page.
