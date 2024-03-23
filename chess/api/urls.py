from django.urls import path
from .views import vitals

urlpatterns = [
    path('vitals/', vitals, name='vitals'),
]
