# forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile  # Import the UserProfile model


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['id_photo']  # Add other fields if needed


class RegistrationForm(UserCreationForm):
    email = forms.EmailField()
    profile_form = UserProfileForm()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']

        if commit:
            user.save()

            # Now handle the UserProfileForm
            profile = self.profile_form.save(commit=False)
            profile.user = user
            profile.save()

        return user


class AddMoneyForm(forms.Form):
    amount = forms.IntegerField(label='Amount', min_value=0)


class BuyCryptoForm(forms.Form):
    quantity = forms.DecimalField(label='Quantity', min_value=0.0001)


class SellCryptoForm(forms.Form):
    quantity = forms.DecimalField(label='Quantity to sell', min_value=0.0001)
