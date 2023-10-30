from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.contrib.auth import logout, login
from .forms import RegistrationForm, UserProfileForm
from .models import UserProfile
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


def home(request):
    return render(request, 'user_management/home.html')


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


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def base(request):
    user = request.user

    try:
        user_profile = UserProfile.objects.get(user=user)
        profile_photo = user_profile.id_photo.url  # Assuming 'id_photo' is the field for the profile photo

    except UserProfile.DoesNotExist:
        profile_photo = None

    return render(request, 'user_management/base.html', {'profile_photo': profile_photo})
