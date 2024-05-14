from django.urls import path
from . import views

urlpatterns = [
    path('', views.ConversationListView.as_view(), name='conversation-list'),
    path('<int:pk>/', views.ConversationDetailView.as_view(), name='conversation-detail'),
    path('messages/', views.MessageCreateView.as_view(), name='message-create'),
    path('messages/<int:pk>/edit/', views.MessageEditView.as_view(), name='message-edit'),
    path('<int:pk>/typing/', views.TypingIndicatorUpdateView.as_view(), name='typing-indicator'),
    path('<int:pk>/read/', views.MarkAsReadView.as_view(), name='mark-as-read'),
]
