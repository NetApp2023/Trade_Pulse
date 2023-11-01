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


class CustomPasswordResetForm(PasswordResetForm):
    username = forms.CharField(label='Username', max_length=150)
    new_password1 = forms.CharField(label='New Password', widget=forms.PasswordInput)
    new_password2 = forms.CharField(label='Confirm New Password', widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data['username']
        # Add any additional validation for the username if needed
        return username

    def clean_new_password2(self):
        new_password1 = self.cleaned_data.get('new_password1')
        new_password2 = self.cleaned_data.get('new_password2')

        if new_password1 and new_password2 and new_password1 != new_password2:
            raise forms.ValidationError('The two password fields must match.')

        return new_password2
