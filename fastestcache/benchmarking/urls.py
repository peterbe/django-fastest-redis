from django.conf import settings
from django.urls import path, re_path

from .views import index, reset, run, summary

_names = "|".join(["random"] + list(settings.CACHE_NAMES))

urlpatterns = [
    path("summary", summary),
    path("reset", reset),
    re_path(r"^run/(?P<cache_name>" + _names + r")$", run),
    path("", index),
]
