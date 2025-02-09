from django.urls import path
from .views import api_root, DomainDb, DomainDbUpsert, DomainCache
from daas_py_config import config
import os

configs = config.get_configs()
DOMAIN = os.getenv("DOMAIN").lower().strip().replace("'", "")

urlpatterns = [
    path("", api_root, name="api-root"),
    path(f"{DOMAIN}/db/", DomainDb.as_view(), name=f"{DOMAIN}-db"),
    path(f"{DOMAIN}/db/upsert/", DomainDbUpsert.as_view(), name=f"{DOMAIN}-db-upsert"),
    path(f"{DOMAIN}/cache", DomainCache.as_view(), name=f"{DOMAIN}-cache"),
]
