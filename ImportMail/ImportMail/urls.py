"""
URL configuration for ImportMail project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import path, re_path
from imap_email.consumers import WSConsumer
from imap_email.views import index, sign_up_by_django, login_up_by_django

# from imap_email.views import get_token

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index),
    path('registration/', sign_up_by_django),
    path('login/', login_up_by_django),
    # path('get-token/', get_token),
]

ws_urlpatterns = [
    re_path('st/', WSConsumer.as_asgi())
]
