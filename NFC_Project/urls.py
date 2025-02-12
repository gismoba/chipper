"""NFC_Project URL Configuration

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
from core.views import handler500, custom_admin_index
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.utils.translation import gettext_lazy as _


admin.site.index_title = "Website Managment"
admin.site.site_header = "Chipper Group"

urlpatterns = [
    path('admin/', custom_admin_index, name='custom_admin_index'),
    path('admin/', admin.site.urls),
    path('', include('users.urls')),
    path('accounts/', include('users.passwords.urls')),
    path('', include('cards.urls')),
    path('hitcount/', include(('hitcount.urls', 'hitcount'), namespace='hitcount')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler500 = handler500
