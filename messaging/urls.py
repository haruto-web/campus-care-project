from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('', views.inbox, name='inbox'),
    path('new/', views.new_message, name='new_message'),
    path('new/<int:recipient_id>/', views.new_message, name='new_message_to'),
    path('<int:conv_id>/', views.conversation, name='conversation'),
    path('<int:conv_id>/poll/', views.poll_messages, name='poll_messages'),
]
