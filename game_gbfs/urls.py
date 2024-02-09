"""
URL configuration for game_gbfs project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
import app.views as views
from app.import_gbfs import gbfs_import

gbfs_import()

urlpatterns = [
    path('admin/', admin.site.urls),
    path('create_game/', views.create_game, name='create_game'),
    path('signup/', views.create_account, name='create_account'),
    path('login/', views.login, name='login'),
    path('check_otp/', views.check_otp, name='check_otp'),
    path('evaluate_game/', views.evaluate_game, name='evaluate_game'),
    path('', views.index, name='index'),
]

