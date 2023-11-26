import os

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout, login, get_user_model

from .forms import RegistrationForm, UserProfileForm, CustomForgotPasswordForm, AddMoneyForm, SellCryptoForm, \
    BuyCryptoForm
from .models import UserProfile, Currency, Cryptocurrency, CryptoPriceHistory, Wallet, Purchase
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
    for crypto in cryptos:
        crypto.converted_price = crypto.price_in_currency(requested_currency)
    return render(request, 'user_management/cryptos.html', {
        'cryptos': cryptos,
        'requested_currency_code': requested_currency,
        'wallet': wallet  # Make sure this name matches the template
    })


def coin_details(request, coin_id):
    # Retrieve the selected coin details from the request
    selected_coin = next((coin for coin in formatted_currencies if coin['coin_id'] == coin_id), None)

    if selected_coin:
        # Remove 'None' values from sparkline data
        sparkline_data = [value for value in selected_coin.get('sparkline') if value is not None]

        # Print cleaned sparkline data to the console
        print(f"Cleaned sparkline data for coin {coin_id}: {sparkline_data}")

        high_price = round(max(map(float, sparkline_data)), 2)
        low_price = round(min(map(float, sparkline_data)), 2)
        average_price = round(sum(map(float, sparkline_data)) / len(sparkline_data), 2) if sparkline_data else 0

        # Pass the selected coin details and cleaned sparkline data to the template
        return render(
            request,
            'user_management/coin_details.html',
            {'coin_details': selected_coin, 'high_price': high_price, 'low_price': low_price,
             'average_price': average_price, 'cleaned_sparkline_data': sparkline_data}
        )
    else:
        # Handle the case where the selected coin is not found
        error_message = f"Coin with ID {coin_id} not found."
        return render(request, 'user_management/coin_details.html', {'error_message': error_message})


def fetch_and_format_currencies():
    coinranking_api_key = "e36c6d68ae02afdfcdc6bba8e8b9ecea12560c1c3840eadf"
    api_url = "https://api.coinranking.com/v2/coins"
    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json().get("data", {}).get("coins", [])
        formatted_currencies = []

        # Create Currency objects with data from the CoinCap API
        for coin in data:
            coin_id = coin.get('uuid', '')
            name = coin.get('name', '')
            symbol = coin.get('symbol', 'BTS')
            icon_url = coin.get('iconUrl', 'https://cdn.coinranking.com/bOabBYkcX/bitcoin_btc.svg')
            rank = coin.get('rank', 0)
            price = float(coin.get('price', 0) or 0)
            market_cap = float(coin.get('marketCap', 0) or 0)
            change = float(coin.get('change', 0) or 0)
            sparkline = coin.get('sparkline', [])
            gradient_start = 50 + change / 2

            # Calculate the percentage change and set the graph color
            graph_color = 'green' if change >= 0 else 'red'

            # Format currency values
            formatted_currency = {
                'coin_id': coin_id,
                'name': name,
                'symbol': symbol,
                'icon_url': icon_url,
                'rank': rank,
                'price': "${}".format(round(price, 2)),
                'market_cap': "${:.2f} billion".format(market_cap / 1e9),
                'change': change,
                'graph_color': graph_color,
                'sparkline': sparkline,
                'gradient_start': gradient_start,
            }

            formatted_currencies.append(formatted_currency)

        return formatted_currencies
    else:
        return []  # Return an empty list or handle the error accordingly


def crypto_detail(request, crypto_name):
    formatted_currencies = fetch_and_format_currencies()
    # Retrieve the selected coin details from the request
    selected_coin = next((coin for coin in formatted_currencies if coin['name'] == crypto_name), None)

    if selected_coin:
        # Remove 'None' values from sparkline data
        sparkline_data = [value for value in selected_coin.get('sparkline') if value is not None]
        high_price = round(max(map(float, sparkline_data)), 2)
        low_price = round(min(map(float, sparkline_data)), 2)
        average_price = round(sum(map(float, sparkline_data)) / len(sparkline_data), 2) if sparkline_data else 0
        print(sparkline_data)

        return render(
            request,
            'user_management/crypto_detail.html',
            {
                'coin_details': selected_coin,
                'coin_name': selected_coin['name'],
                'high_price': high_price,
                'low_price': low_price,
                'average_price': average_price,
                'cleaned_sparkline_data': sparkline_data,
            }
        )


@login_required
def add_money(request):
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = AddMoneyForm(request.POST)
        if form.is_valid():
            amount = int(form.cleaned_data.get('amount'))
            wallet.amount += amount
            wallet.save()
            return redirect('home')  # Redirect to a success page or home
    else:
        form = AddMoneyForm()

    return render(request, 'user_management/add_money.html', {'form': form, 'wallet': wallet})


@login_required
def buy_crypto(request, crypto_id):
    crypto = get_object_or_404(Cryptocurrency, pk=crypto_id)
    wallet, created = Wallet.objects.get_or_create(user=request.user)  # Get the wallet for the logged-in user

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
                    purchase_price=total_cost,
                    transaction_type="Bought"
                )
                return redirect('home')  # Adjust the 'payment:home' to your project's URL name
            else:
                form.add_error(None, 'Insufficient funds in your wallet.')
    else:
        form = BuyCryptoForm()

    return render(request, 'user_management/buy.html', {
        'crypto': crypto,
        'wallet': wallet,
        'form': form
    })


@login_required()
def sell_crypto(request, crypto_id):
    crypto = get_object_or_404(Cryptocurrency, pk=crypto_id)
    wallet, created = Wallet.objects.get_or_create(user=request.user)  # Get the wallet for the logged-in user

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
                    purchase_price=total_revenue,
                    transaction_type="Sold"
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
                return redirect('home')  # Adjust the URL name to your project's home URL name
            else:
                # Handle case where user tries to sell more than they own
                form.add_error(None, 'You cannot sell more than you own.')
    else:
        form = SellCryptoForm()

    return render(request, 'user_management/sell.html', {
        'crypto': crypto,
        'wallet': wallet,
        'form': form,
        'total_quantity_owned': total_quantity_owned
    })


@login_required
def Payment_History(request):
    purchases = Purchase.objects.all()
    wallet = Wallet.objects.first()
    context = {'purchases': purchases,
               'wallet': wallet}
    return render(request, 'user_management/Payment_History.html', context)
