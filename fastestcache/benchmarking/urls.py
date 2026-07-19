from django.conf import settings
from django.urls import path

from .views import run, summary

cache_names = "|".join(settings.CACHE_NAMES)

urlpatterns = [
    path("summary", summary),
    path("<str:cache_name>", run),
]
