from django.urls import path
from .views import vitals, set_csrf_token, get_csrf
from .validation_views import validate_move

urlpatterns = [
    path('vitals/', vitals, name='vitals'),
    path('set-csrf-token/', set_csrf_token, name='set-csrf-token'),
    path('get-csrf-token/', get_csrf, name='get-csrf-token'),
    path('validate-move/', validate_move, name='validate-move')
    
]
