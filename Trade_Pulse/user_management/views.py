import json
import os
from datetime import datetime, timedelta
from io import BytesIO

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout, login, get_user_model
import matplotlib.pyplot as plt
import base64
import matplotlib.dates as mdates

from django.shortcuts import render
import requests
from django.utils import timezone

from .forms import RegistrationForm, UserProfileForm, CustomForgotPasswordForm, AddMoneyForm, SellCryptoForm, \
    BuyCryptoForm, FeedbackForm
from .models import UserProfile, Currency, Cryptocurrency, CryptoPriceHistory, Wallet, Purchase, Feedback
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages

import os
from django.conf import settings
import requests


def registration(request):
    if request.method == 'POST':
        user_form = RegistrationForm(request.POST)
        profile_form = UserProfileForm(request.POST, request.FILES)

        try:
            if user_form.is_valid() and profile_form.is_valid():
                user = user_form.save()

                # Check if UserProfile already exists for the user
                try:
                    profile = UserProfile.objects.get(user=user)
                except UserProfile.DoesNotExist:
                    profile = UserProfile(user=user)

                profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
                profile_form.save()

                # login(request, user)
                print("User registered successfully")
                return redirect('login')  # Redirect to the user's dashboard after registration
        except IntegrityError as e:
            # Handle the IntegrityError, e.g., username or email already exists
            error_message = "Username or email already exists. Please choose a different one."
            user_form.add_error(None, error_message)
            print(f"IntegrityError: {e}")

    else:
        user_form = RegistrationForm()
        profile_form = UserProfileForm()

    return render(request, 'user_management/register.html', {'user_form': user_form, 'profile_form': profile_form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')  # Change 'dashboard' to your actual dashboard URL
    else:
        form = AuthenticationForm()

    return render(request, 'user_management/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('base')


def base(request):
    crypto_info = Cryptocurrency.objects.all().order_by('-price_usd')
    return render(request, 'user_management/base.html', {'cryptos': crypto_info})


def forgot_password(request):
    if request.method == 'POST':
        form = CustomForgotPasswordForm(request.POST)
        if form.is_valid():
            print("Form is valid")
            username = form.cleaned_data['username']
            new_password = form.cleaned_data['new_password']

            # Check if the user with the provided username exists
            User = get_user_model()
            try:
                user = User.objects.get(username=username)

                # Update the user's password
                user.set_password(new_password)
                user.save()

                messages.success(request, "Password has been reset successfully.")
                return redirect('login')
            except User.DoesNotExist:
                messages.error(request, "No user found with the provided username.")
        else:
            print("Form errors:", form.errors)
    else:
        form = CustomForgotPasswordForm()

    return render(request, 'user_management/forgot_password.html', {'form': form})


formatted_currencies = []


@login_required
def home(request):
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    requested_currency = request.GET.get('currency', 'CAD')
    cryptos = Cryptocurrency.objects.all().order_by('-price_usd')
    currencies = Currency.objects.all()
    currency_rates = {currency.code: currency.rate_to_usd for currency in currencies}
    rate_to_usd = currency_rates.get(requested_currency, 1)  # Default conversion rate
    for crypto in cryptos:
        crypto.price_usd = crypto.price_usd * rate_to_usd
        crypto.market_cap = crypto.market_cap * rate_to_usd
        crypto.volume = crypto.volume * rate_to_usd

    return render(request, 'user_management/cryptos.html', {
        'cryptos': cryptos,
        'requested_currency_code': requested_currency,
        'currencies': currencies,
        'wallet': wallet  # Make sure this name matches the template
    })


@login_required
def add_money(request):
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    msg = ""
    if request.method == 'POST':
        form = AddMoneyForm(request.POST)
        if form.is_valid():
            amount = int(form.cleaned_data.get('amount'))
            wallet.amount += amount
            wallet.save()
            msg = "Wallet Top-Up Success"
        else:
            msg = "Wallet Top-Up Failed. Please check the form inputs."
    else:
        form = AddMoneyForm()

    return render(request, 'user_management/add_money.html', {'form': form, 'wallet': wallet, 'msg': msg})


@login_required
def buy_crypto(request, crypto_id):
    crypto = get_object_or_404(Cryptocurrency, pk=crypto_id)
    wallet, created = Wallet.objects.get_or_create(user=request.user)  # Get the wallet for the logged-in user
    buy_msg = ''
    p_date = timezone.now()
    if request.method == 'POST':
        form = BuyCryptoForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            total_cost = quantity * crypto.price_usd
            if wallet.amount >= total_cost:
                wallet.amount -= total_cost
                wallet.save()
                Purchase.objects.create(
                    user=request.user,
                    crypto=crypto,
                    quantity=quantity,
                    trans_quantity=quantity,
                    purchase_price=total_cost,
                    transaction_type="Bought",
                    purchase_date=p_date
                )
                return redirect('home')  # Adjust the 'payment:home' to your project's URL name
            else:
                buy_msg = "Insufficient funds in your wallet."
                form.add_error(None, 'Insufficient funds in your wallet.')
    else:
        form = BuyCryptoForm()

    return render(request, 'user_management/buy.html', {
        'crypto': crypto,
        'wallet': wallet,
        'form': form,
        'msg': buy_msg
    })


@login_required()
def sell_crypto(request, crypto_id):
    crypto = get_object_or_404(Cryptocurrency, pk=crypto_id)
    wallet, created = Wallet.objects.get_or_create(user=request.user)  # Get the wallet for the logged-in user
    sell_msg = ''
    p_date = timezone.now()

    # Retrieve the total quantity owned by summing all purchases for the current user
    aggregated = Purchase.objects.filter(user=request.user, crypto=crypto).aggregate(total_quantity=Sum('quantity'))
    total_quantity_owned = aggregated.get('total_quantity', 0) or 0

    if request.method == 'POST':
        form = SellCryptoForm(request.POST)
        if form.is_valid():
            quantity_to_sell = form.cleaned_data['quantity']
            if quantity_to_sell <= total_quantity_owned:
                total_revenue = quantity_to_sell * crypto.price_usd
                wallet.amount += total_revenue
                wallet.save()

                Purchase.objects.create(
                    user=request.user,
                    crypto=crypto,
                    trans_quantity=quantity_to_sell,
                    purchase_price=total_revenue,
                    transaction_type="Sold",
                    purchase_date=p_date
                )

                # Update the Purchase records for the current user. This logic assumes that you sell the oldest purchases first.
                purchases = Purchase.objects.filter(user=request.user, crypto=crypto).order_by('purchase_date')
                for purchase in purchases:
                    if quantity_to_sell <= purchase.quantity:
                        purchase.quantity -= quantity_to_sell
                        purchase.save()
                        break
                    else:
                        quantity_to_sell -= purchase.quantity
                        purchase.quantity = 0
                        purchase.save()
                        if purchase.quantity == 0:
                            purchase.delete()  # Optionally delete the purchase if quantity is zero

                # Redirect to a success page or home
                return redirect('home')
                # Adjust the URL name to your project's home URL name
            else:
                # Handle case where user tries to sell more than they own
                sell_msg = "Insufficient Number of Coins"
                form.add_error(None, 'You cannot sell more than you own.')
    else:
        form = SellCryptoForm()

    return render(request, 'user_management/sell.html', {
        'crypto': crypto,
        'wallet': wallet,
        'form': form,
        'total_quantity_owned': total_quantity_owned,
        'msg': sell_msg
    })


@login_required
def Payment_History(request):
    purchases = Purchase.objects.all()
    wallet = Wallet.objects.first()
    context = {'purchases': purchases,
               'wallet': wallet}
    return render(request, 'user_management/Payment_History.html', context)


def currency_view(request):
    requested_currency_code = request.GET.get('currency', 'USD')  # Default to USD if no currency selected
    cryptos = Cryptocurrency.objects.all()  # Assuming you have a model named Crypto

    for crypto in cryptos:
        crypto.converted_price = convert_currency(crypto.price_usd, requested_currency_code)
        crypto.market_cap = convert_currency(crypto.market_cap, requested_currency_code)
        crypto.volume = convert_currency(crypto.volume, requested_currency_code)

    return render(request, 'your_template.html', {
        'cryptos': cryptos,
        'requested_currency_code': requested_currency_code
    })


def convert_currency(amount, currency_code):
    # Your currency conversion logic here
    # This will depend on how you're able to retrieve conversion rates
    # Maybe you have a pre-defined dictionary of rates or use an API
    conversion_rate = get_conversion_rate(currency_code)
    return amount * conversion_rate


def get_conversion_rate(currency_code):
    # Retrieve the conversion rate for the given currency code
    # This is a placeholder for the actual rate retrieval logic
    rates = {'USD': 1, 'CAD': 0.8, 'EUR': 1.2, 'INR': 0.014}  # Example rates
    return rates.get(currency_code, 1)  # Default to 1 if currency not found


def generate_price_history_graph(request, crypto_id):
    crypto = Cryptocurrency.objects.get(pk=crypto_id)

    price_history = crypto.price_history

    timestamps = [datetime.fromtimestamp(item['timestamp']) for item in price_history]
    prices = [float(item['price']) for item in price_history]

    plt.figure(figsize=(10, 5))
    plt.plot(timestamps, prices, linestyle='-', color='blue')

    # Clean up the x-axis dates
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())

    # Set limits for x-axis to add padding on both sides
    plt.xlim(min(timestamps) - timedelta(days=1), max(timestamps) + timedelta(days=1))

    plt.xlabel('Date')
    plt.ylabel('Price (USD)')
    plt.title(f'{crypto.name} Price History')
    plt.grid(True)

    buffer = BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')  # 'bbox_inches' ensures no cut-off
    plt.close()

    # Encode the buffer's contents in base64
    graph_data = base64.b64encode(buffer.getvalue()).decode('utf-8')

    # Render the graph template with context data
    context = {
        'crypto_name': crypto.name,
        'graph_data': graph_data,
    }
    return render(request, 'user_management/graph.html', context)


@login_required
def feedback_view(request):
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = FeedbackForm()
    feedback_msg = Feedback.objects.all()
    return render(request, 'user_management/feedback_form.html', {'form': form, 'feedback_msg': feedback_msg, 'wallet': wallet})
