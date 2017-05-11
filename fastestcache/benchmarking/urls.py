from django.conf.urls import url
from django.conf import settings
from .views import run, summary


rest = '|'.join(settings.CACHE_NAMES)

urlpatterns = [
    url(r'(?P<cache_name>(random|{}))'.format(rest), run),
    url(r'summary', summary),
]
