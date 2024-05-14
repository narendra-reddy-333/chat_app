from django.urls import path
from .views import UserCreateView, UserDetailView, LoginView

urlpatterns = [
    path('register/', UserCreateView.as_view(), name='user-create'),
    path('<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('login/', LoginView.as_view(), name='login'),
]
