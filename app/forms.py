from django import forms
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class UploadImageForm(forms.Form):
    title = forms.CharField(max_length=50)
    image = forms.ImageField()

class RegisterForm(UserCreationForm):
    email = forms.EmailField()
    # game_name = forms.RegexField(r"\w+", "Your in game name should be from 3 to 30 characters long.")
    game_name = forms.RegexField(r"\w{3,30}",
                                 error_messages={
            'invalid': ("Your ingame name should be contain  3-30 alphanumeric characters ")
        })
    class Meta:
        model = User
        fields = ["username","game_name","email","password1","password2"]
