
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render
from django.views.generic.edit import CreateView
from django.contrib.auth.models import User


class UserCreateView(CreateView):
    form_class = UserCreationForm
    template_name = "register_user.html"
    success_url = "/user/login"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #self.fields['title'].widget.attrs['class'] = 'my_class'


class UserLoginView(LoginView):
    template_name = "login.html"
