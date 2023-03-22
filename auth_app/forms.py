from django import forms
from allauth.account.forms import SignupForm
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from auth_app.models import MyUser


class CustomSignupForm(SignupForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)


class ProfileForm(forms.Form):
    avatar = forms.ImageField(required=False,widget=forms.FileInput(attrs={'class': 'button settings w-button', 'name': 'profile_picture'}))
    name = forms.CharField(required=True,max_length=155, widget=forms.TextInput(attrs={'class': 'text-input filled w-input', 'name': 'name'}))
    email = forms.EmailField(max_length=155, widget=forms.TextInput(attrs={'class': 'text-input filled w-input', 'name': 'profile-email', 'disabled': 'true'}))
    username = forms.CharField(required=False, validators=[],max_length=155, widget=forms.TextInput(attrs={'class': 'text-input filled w-input', 'name': 'username'}))
    bio = forms.CharField(required=False,max_length=355, widget=forms.TextInput(attrs={'class': 'text-input filled w-input', 'name': 'bio'}))

    def check_coincidence(self, username, user_profile):
        list_of_usernames = []
        for user in MyUser.objects.all():
            list_of_usernames.append(user.username)
        if username != user_profile.user.username:
            if username in list_of_usernames:
                return False
        return True


class SupportForm(forms.Form):
    first_name = forms.CharField(required=True, max_length=256, widget=forms.TextInput(attrs={'class': 'text-input w-input', 'name': 'first_name', 'placeholder': 'Your first name'}))
    last_name = forms.CharField(required=True, max_length=256, widget=forms.TextInput(attrs={'class': 'text-input w-input', 'name': 'last_name', 'placeholder': 'Your last name'}))
    email = forms.EmailField(required=True, max_length=256, widget=forms.TextInput(attrs={'class': 'text-input w-input', 'name': 'email', 'placeholder': 'example@email.com', 'disabled': 'true'}))
    phone_number = forms.CharField(required=False, max_length=256, widget=forms.TextInput(attrs={'class': 'text-input w-input', 'name': 'phone_number', 'placeholder': '027 123 1234'}))
    appeal_body = forms.CharField(required=True, max_length=5000, widget=forms.Textarea(attrs={'class': 'text-area full-width w-input', 'name': 'appeal', 'placeholder': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse varius enim in eros elementum tristique.'}))


class SimpleSignupForm(SignupForm):
    first_name = forms.CharField(max_length=155, label='Name')

    def save(self, request):
        user = super(SimpleSignupForm, self).save(request)
        user.phone = self.cleaned_data['first_name']
        user.save()
        return user