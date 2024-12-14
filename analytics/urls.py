from django.urls import path
from .views import random_data_view


urlpatterns=[
    path('analytics',random_data_view)
]