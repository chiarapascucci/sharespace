"""sharespace_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.conf.urls import url
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, reverse
from django.urls import include
from sharespace import views
from django.conf import settings 
from django.conf.urls.static import static
from registration.backends.default.views import ActivationView


class MyActivationView(ActivationView):
    def get_success_url(self, user):
        print("in customer activation view")
        return reverse('sharespace:complete_profile')


urlpatterns = [
    path('', views.index, name='index'),
    path('sharespace/', include('sharespace.urls')),
    path('admin/', admin.site.urls),
    path('accounts/activate/<activation_key>/', MyActivationView.as_view(), name='registration_activate'),
    path('accounts/', include('registration.backends.default.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
