from django.urls import path
from . import views

app_name = 'ai_assistant'

urlpatterns = [
    path('counselor/', views.counselor_chat_view, name='counselor_chat_view'),
    path('admin/', views.admin_chat_view, name='admin_chat_view'),
    path('counselor/chat/', views.counselor_chat, name='counselor_chat'),
    path('admin/chat/', views.admin_chat, name='admin_chat'),
]
