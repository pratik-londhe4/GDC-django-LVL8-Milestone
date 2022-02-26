from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views


urlpatterns = [
    path("signup/", views.UserCreateView.as_view()),
    path("login/", views.UserLoginView.as_view()),
    path("logout/", LogoutView.as_view())


]
