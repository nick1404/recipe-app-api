from django.urls import path
from . import views

app_name = ' user'

urlpatterns = [
    path('create/', views.CreateUserView.as_view(), name='create'), # Connect the view to the URL adress
    path('token/', views.CreateTokenView.as_view(), name='token'),
    path('me/', views.ManageUserView.as_view(), name='me'),
]