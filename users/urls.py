from django.urls import path
from .views import SignupView, LoginView, GetUsers

urlpatterns = [
    path('register/', SignupView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('userslist/', GetUsers.as_view(), name='get-users'),
]
