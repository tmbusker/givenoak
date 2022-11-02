from django.urls import path
from jinji.admin import jinjiSite
from jinji.views import select_ido_type


urlpatterns = [
    path('select_ido_type/', select_ido_type, name='select_ido_type'),
    path('', jinjiSite.urls, name='jinji'),
]
