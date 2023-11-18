import paypalrestsdk
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.contrib.auth import logout, login, get_user_model
from django.utils import timezone
from paypalrestsdk import Payment

from Trade_Pulse import settings
from .forms import RegistrationForm, UserProfileForm, CustomForgotPasswordForm, BuyCoinsForm
from .models import UserProfile, Currency, Payment
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
import requests
from decimal import Decimal
from django.db import IntegrityError, transaction


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
    return redirect('home')


@login_required
def base(request):
    user = request.user

    try:
        user_profile = UserProfile.objects.get(user=user)
        profile_photo = user_profile.id_photo.url

    except UserProfile.DoesNotExist:
        profile_photo = None

    return render(request, 'user_management/base.html', {'profile_photo': profile_photo})


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


def home(request):

    formatted_currencies = fetch_and_format_currencies()
    # Pass all currencies data to the template
    return render(
        request,
        'user_management/home.html',
        {'currencies': formatted_currencies}
    )


def coin_details(request, coin_id):
    formatted_currencies = fetch_and_format_currencies()
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

        # Dummy exchange rate data (replace with actual data)
        exchanges = [
            {"name": "Binance", "btc_price": 35370.16, "trade_volume": "3.02 billion",
             "iconUrl": '/static/user_management/binance.png'},
            {"name": "Bitforex", "btc_price": 35382.86, "trade_volume": "780.33 million",
             "iconUrl": '/static/user_management/bitforex.png'},
            {"name": "BitMart", "btc_price": 35407.29, "trade_volume": "544.68 million",
             "iconUrl": '/static/user_management/bitmart.png'},
            {"name": "Coinbase Pro", "btc_price": 35366.77, "trade_volume": "481.51 million",
             "iconUrl": '/static/user_management/coinbase.png'},
            {"name": "Bybit", "btc_price": 35362.33, "trade_volume": "471.73 million",
             "iconUrl": '/static/user_management/bybit.png'},
            {"name": "OKX", "btc_price": 35344.44, "trade_volume": "462.19 million",
             "iconUrl": '/static/user_management/okx.png'},
            {"name": "DigiFinex", "btc_price": 35343.19, "trade_volume": "418.94 million",
             "iconUrl": '/static/user_management/digifinex.png'},
            {"name": "Crypto.com", "btc_price": 35357.06, "trade_volume": "390.91 million",
             "iconUrl": '/static/user_management/crypto.png'},
            {"name": "Bitget", "btc_price": 35379.59, "trade_volume": "331.57 million",
             "iconUrl": '/static/user_management/bitget.jpg'},
            {"name": "MEXC Global", "btc_price": 35357.32, "trade_volume": "339.19 million",
             "iconUrl": '/static/user_management/MEXC.jpg'},
        ]

        for exchange in exchanges:
            exchange['iconUrl'] = request.build_absolute_uri(exchange['iconUrl'])

        top_users = User.objects.order_by('-date_joined')[:5]

        # Create a dummy buyers list for the selected coin
        selected_coin_buyers = [
            {"user": {"username": user.username}, "amount": 120} for user in top_users
        ]

        # Combine the dummy buyers lists
        all_buyers = selected_coin_buyers

        # Sort the combined list by the 'amount' key in descending order
        top_buyers = sorted(all_buyers, key=lambda x: x['amount'], reverse=True)[:5]

        crypto_api_url = f"https://api.coingecko.com/api/v3/simple/price?ids={selected_coin['name']}&vs_currencies=usd"
        crypto_currencies = ['usd', 'eur', 'gbp']  # Add more currencies as needed

        # Fetch cryptocurrency rates for each currency
        crypto_rates = {}
        for currency in crypto_currencies:
            params = {
                'ids': selected_coin['name'],
                'vs_currencies': currency,
            }
            crypto_response = requests.get(crypto_api_url, params=params)

            if crypto_response.status_code == 200:
                rate = crypto_response.json().get(selected_coin['name'], {}).get(currency)
                crypto_rates[currency] = rate
            else:
                crypto_rates[currency] = 'N/A'

            # Pass the selected coin details, cleaned sparkline data, and exchange rate data to the template
            return render(
                request,
                'user_management/coin_details.html',
                {
                    'coin_details': selected_coin,
                    'high_price': high_price,
                    'low_price': low_price,
                    'average_price': average_price,
                    'exchanges': exchanges,
                    'top_buyers': top_buyers,
                    'crypto_rates': crypto_rates,
                    'crypto_currencies': crypto_currencies,
                    'cleaned_sparkline_data': sparkline_data,
                }
            )
    else:
        # Handle the case where the selected coin is not found
        error_message = f"Coin with ID {coin_id} not found."
        return render(request, 'user_management/coin_details.html', {'error_message': error_message})


@login_required
def user_profile(request):
    global total_amount, selected_coin_data, pc, payment_history
    total_amount = 0
    user = request.user
    coin_id = request.GET.get('coin_id')
    user_profile = UserProfile.objects.get(user=user)
    formatted_currencies = fetch_and_format_currencies()
    try:
        profile_photo = user_profile.id_photo.url

        # Get other user details
        username = user.username
        email = user.email

        payment_history = Payment.objects.filter(user=user)
        for c in payment_history:
            print(c.transaction_id)

        # Check if the coin_id parameter is present in the URL
        selected_coin_data = next((coin for coin in formatted_currencies if coin['coin_id'] == coin_id), None)

        # Handle the buy coins form submission
        if request.method == 'POST':
            form = BuyCoinsForm(request.POST)
            if form.is_valid():
                amount = form.cleaned_data['amount']

                # Check if selected_coin_data is not None
                if selected_coin_data is not None:
                    price_per_unit = Decimal(selected_coin_data['price'].replace(',', '').replace('$', ''))
                    total_amount = price_per_unit * amount

                    # Add the selected coin to the user's purchased coins
                    selected_coin, created = Currency.objects.get_or_create(
                        uuid=selected_coin_data['coin_id'],
                        defaults={
                            'symbol': selected_coin_data['symbol'],
                            'name': selected_coin_data['name'],
                            'color': selected_coin_data['graph_color'],
                            'icon_url': selected_coin_data['icon_url'],
                            'market_cap': total_amount,  # Set appropriate values or adjust the model
                            'price': Decimal(selected_coin_data['price'].replace(',', '').replace('$', '')),
                            'listed_at': timezone.now(),
                            'tier': 0,  # Set appropriate values or adjust the model
                            'change': 0,  # Set appropriate values or adjust the model
                            'rank': price_per_unit,  # Set appropriate values or adjust the model
                            'sparkline': None,  # Set appropriate values or adjust the model
                            'low_volume': False,  # Set appropriate values or adjust the model
                            'volume_24hr': 0,  # Set appropriate values or adjust the model
                            'btc_price': 0  # Set appropriate values or adjust the model
                        }
                    )

                    try:
                        with transaction.atomic():
                            user_profile.purchased_coins.add(selected_coin)
                            user_profile.save()
                            print("UserProfile saved successfully")
                    except IntegrityError as e:
                        print(f"IntegrityError saving user profile: {e}")

                    # Redirect to the payments page after a successful purchase
                    return redirect('payment_view', coin_id=coin_id, total_amount=total_amount)
                else:
                    messages.error(request, "Invalid coin selected for purchase.")
            else:
                messages.error(request, "Invalid form submission.")
        else:
            form = BuyCoinsForm()

        if selected_coin_data is None:
            messages.error(request, "Invalid coin selected for purchase.")

    except UserProfile.DoesNotExist:
        profile_photo = None
        form = None
        selected_coin = None
        username = None
        email = None

    return render(
        request,
        'user_management/user_profile.html',
        {
            'profile_photo': profile_photo,
            'buy_coins_form': form,
            'total_amount': total_amount,
            'selected_coin': selected_coin_data,
            'username': username,
            'email': email,
            'user_profile': user_profile,
            'payment_history': payment_history,
        }
    )


paypalrestsdk.configure({
    "mode": "sandbox",  # Change to "live" for production
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_SECRET,
})


def payment_view(request, coin_id, total_amount):
    try:
        total_amount = float(total_amount)
    except ValueError:
        # Handle the case where total_amount is not a valid float
        # You might want to redirect or display an error message
        pass

    paypal_client_id = settings.PAYPAL_CLIENT_ID
    paypal_secret = settings.PAYPAL_SECRET

    # Create a PayPal payment
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal",
        },
        "transactions": [
            {
                "amount": {
                    "total": str(total_amount),
                    "currency": "USD",
                },
            },
        ],
        "redirect_urls": {
            "return_url": "http://localhost:8000/payment_success/",
            "cancel_url": "http://localhost:8000/payment_cancel/",
        },
    })

    if payment.create():
        # Save the payment details to your local Payment model
        Payment.objects.create(
            user=request.user,
            amount=total_amount,
            currency=Currency.objects.get(uuid=coin_id),
            payment_date=timezone.now(),
            transaction_id=payment.id,
        )
        print(Payment)
    else:
        print(payment.error)
        # Handle payment creation error

    return render(request, 'user_management/payment.html',
                  {'paypal_client_id': paypal_client_id, 'coin_id': coin_id, 'total_amount': total_amount})


def payment_success(request):
    return render(request, 'user_management/payment_success.html')

# def payment_success(request):
#     if request.method == 'GET':
#         payment_id = request.GET.get('paymentId')
#         print(payment_id)
#         if payment_id:
#             # Fetch the payment from PayPal
#             payment_response = paypalrestsdk.Payment.find(payment_id)
#             print(payment_response)
#             if payment_response.success():
#                 # Get the associated payment model instance
#                 payment = Payment.objects.get(transaction_id=payment_id)
#                 print(payment)
#                 # Update the payment model with the captured transaction ID
#                 captured_transaction_id = payment_response.transactions[0].related_resources[0].sale.id
#                 payment.captured_transaction_id = captured_transaction_id
#                 payment.save()
#
#                 print(captured_transaction_id)
#
#                 messages.success(request, "Payment captured successfully.")
#
#                 # Redirect to the user_profile page with the updated payment history
#                 return redirect('user_profile')
#             else:
#                 messages.error(request,
#                                "Failed to capture payment. PayPal API error: {}".format(payment_response.error))
#
#     return render(request, 'user_management/payment_success.html')
