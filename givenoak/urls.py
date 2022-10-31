"""givenoak URL Configuration

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
from django.urls import path
from django.views.generic.base import RedirectView
from cmm.admin import cmmSite
from mst.admin import mstSite
from jinji.admin import jinjiSite


urlpatterns = [
    path('admin/', admin.site.urls),
    # path('commonsite/', cmmSite.urls, name='commonsite'),
    # path('mastersite/', mstSite.urls, name='mastersite'),
    path('jinji/', jinjiSite.urls, name='jinji'),
    path('', RedirectView.as_view(url='/jinji')),
    # path('', RedirectView.as_view(url='/admin')),
]
