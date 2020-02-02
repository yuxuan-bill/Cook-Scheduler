from django.urls import path
from . import views

app_name = 'cookschedule'

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('change_password/', views.change_password, name="change_password"),
    path('user_stat/', views.user_stat, name="user_stat")
]