"""email_sender URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.urls import path, include, re_path

from rest_framework.routers import DefaultRouter

from emails_controller.views import CancelarInscrição, CancelarInscricaoPage, PremioMgaPage

router = DefaultRouter()

urlpatterns = [
    path('email_sender/', admin.site.urls),
    path('', include(router.urls)),
    path(r'unsubscribe/', CancelarInscrição.as_view(), name='unsubscribe'),
    re_path(r'premio_mga/$', PremioMgaPage.as_view(), name='premio_mga'),
    path(r'cancelar_inscricao/', CancelarInscricaoPage.as_view(), name='cancelar_inscricao')
]
