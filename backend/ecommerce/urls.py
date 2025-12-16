"""
URL configuration for ecommerce project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path, include
from django.conf import settings
from core.views import CreatePaymentIntentView

from core import views as core_views

urlpatterns = [
    path("", core_views.home, name="home"),
    path("admin/", admin.site.urls),
    path(
        "api/v1/create-payment-intent/",
        CreatePaymentIntentView.as_view(),
        name="create-payment-intent",
    ),
]

# Debug toolbar uniquement si:
# - DEBUG est True
# - et l'app "debug_toolbar" est dans INSTALLED_APPS
if settings.DEBUG and "debug_toolbar" in settings.INSTALLED_APPS:
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ]
