from django.urls import path
from .views import api_root, DomainDb, DomainDbUpsert, DomainCache
from daas_py_config import config
import os

configs = config.get_configs()

urlpatterns = [
    path('', api_root, name='api-root'),
    path(f'{os.getenv("DOMAIN").lower()}/db/', DomainDb.as_view(), name=f'{os.getenv("DOMAIN").lower()}-db'),
    path(f'{os.getenv("DOMAIN").lower()}/db/upsert/', DomainDbUpsert.as_view(), name=f'{os.getenv("DOMAIN").lower()}-db-upsert'),
    path(f'{os.getenv("DOMAIN").lower()}/cache', DomainCache.as_view(), name=f'{os.getenv("DOMAIN").lower()}-cache'),
]
