# forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm
from django.contrib.auth.models import User
from .models import UserProfile  # Import the UserProfile model


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['id_photo']  # Add other fields if needed
        # widgets = {
        #     'id_photo': forms.ClearableFileInput(attrs={'required': False}),  # Add this line to make it not required
        # }


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


class CustomForgotPasswordForm(PasswordResetForm):
    username = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)  # You can make it required if necessary
    new_password = forms.CharField(widget=forms.PasswordInput, label='New Password')
    confirm_password = forms.CharField(widget=forms.PasswordInput, label='Confirm Password')

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError("New password and confirm password do not match.")

        return cleaned_data


class AddMoneyForm(forms.Form):
    amount = forms.IntegerField(label='Amount', min_value=0)


class BuyCryptoForm(forms.Form):
    quantity = forms.DecimalField(label='No: of Coins', min_value=0.0001)


class SellCryptoForm(forms.Form):
    quantity = forms.DecimalField(label='Coins to be Sold', min_value=0.0001)
