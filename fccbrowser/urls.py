"""fccbrowser URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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

from browser import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name="index"),
    path('szukaj', views.search, name="search"),
    path('stream/<path:path>', views.stream_file, name="stream_file"),
    path('pobierz/<path:path>', views.get_file, name="get_file"),
    path('przegladaj', views.browse, name="browser"),
    path('przegladaj/<path:path>', views.browse, name="browser_path"),
    path('pokaz/<path:path>', views.show, name="show")
]
