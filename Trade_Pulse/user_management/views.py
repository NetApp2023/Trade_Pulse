from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout, login
from .forms import RegistrationForm, UserProfileForm, AddMoneyForm, BuyCryptoForm, SellCryptoForm
from .models import UserProfile, Wallet, Purchase, Crypto
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


@login_required
def home(request):
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    cryptos = Crypto.objects.all()
    return render(request, 'user_management/home.html', {'wallet': wallet, 'cryptos': cryptos})


@login_required()
def base(request):
    wallet = Wallet.objects.first()
    return render(request, 'user_management/base.html', {'wallet': wallet})


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
    crypto = get_object_or_404(Crypto, pk=crypto_id)
    wallet, created = Wallet.objects.get_or_create(user=request.user)  # Get the wallet for the logged-in user

    if request.method == 'POST':
        form = BuyCryptoForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            total_cost = quantity * crypto.price
            if wallet.amount >= total_cost:
                wallet.amount -= total_cost
                wallet.save()
                Purchase.objects.create(
                    user=request.user,
                    crypto=crypto,
                    quantity=quantity,
                    purchase_price=crypto.price,
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
    crypto = get_object_or_404(Crypto, pk=crypto_id)
    wallet, created = Wallet.objects.get_or_create(user=request.user)  # Get the wallet for the logged-in user

    # Retrieve the total quantity owned by summing all purchases for the current user
    aggregated = Purchase.objects.filter(user=request.user, crypto=crypto).aggregate(total_quantity=Sum('quantity'))
    total_quantity_owned = aggregated.get('total_quantity', 0) or 0

    if request.method == 'POST':
        form = SellCryptoForm(request.POST)
        if form.is_valid():
            quantity_to_sell = form.cleaned_data['quantity']
            if quantity_to_sell <= total_quantity_owned:
                total_revenue = quantity_to_sell * crypto.price
                wallet.amount += total_revenue
                wallet.save()

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

                login(request, user)
                print("User registered successfully")
                return redirect('home')  # Redirect to the user's dashboard after registration
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


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


def base(request):
    user = request.user

    try:
        user_profile = UserProfile.objects.get(user=user)
        profile_photo = user_profile.id_photo.url  # Assuming 'id_photo' is the field for the profile photo

    except UserProfile.DoesNotExist:
        profile_photo = None

    return render(request, 'user_management/base.html', {'profile_photo': profile_photo})
