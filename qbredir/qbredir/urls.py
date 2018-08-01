"""qbredir URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/dev/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
import qbredir.views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$',csrf_exempt(qbredir.views.home),name="home"),
    url(r'^setdata/$',csrf_exempt(qbredir.views.setdata),name="setdata"),
    url(r'^getdata/$',csrf_exempt(qbredir.views.getdata),name="getdata"),
    url(r'^files$',csrf_exempt(qbredir.views.files),name="files"),
    url(r'^getqueue',csrf_exempt(qbredir.views.getqueue),name="getqueue"),
    url(r'^settorrentdata',csrf_exempt(qbredir.views.settorrentdata),name ="setttorrentdata"),
]
