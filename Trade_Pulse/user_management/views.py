from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.contrib.auth import logout, login, get_user_model
from .forms import RegistrationForm, UserProfileForm, CustomForgotPasswordForm
from .models import UserProfile, Currency
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
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


formatted_currencies = []


def home(request):
    # Your CoinRanking API key
    coinranking_api_key = "e36c6d68ae02afdfcdc6bba8e8b9ecea12560c1c3840eadf"

    # Fetch data from CoinCap API
    api_url = "https://api.coinranking.com/v2/coins"
    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json().get("data", {}).get("coins", [])

        # Clear existing Currency data
        Currency.objects.all().delete()

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

        # Pass all currencies data to the template
        return render(
            request,
            'user_management/home.html',
            {'currencies': formatted_currencies}
        )
    else:
        # Handle API error
        error_message = f"Failed to fetch data from CoinCap API. Status Code: {response.status_code}"
        return render(request, 'user_management/home.html', {'error_message': error_message})


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
            {'coin_details': selected_coin,'high_price':high_price,'low_price':low_price,'average_price':average_price, 'cleaned_sparkline_data': sparkline_data }
        )
    else:
        # Handle the case where the selected coin is not found
        error_message = f"Coin with ID {coin_id} not found."
        return render(request, 'user_management/coin_details.html', {'error_message': error_message})

