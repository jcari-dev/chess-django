from django.urls import path
from .views import vitals, set_csrf_token, get_csrf
from .validation_views import validate_move
from .moves_views import get_valid_moves, check_turn, check_move_continuation
from .room_views import create_room, join_room, check_room, update_match, get_fen, get_turn

urlpatterns = [
    
    path('vitals/', vitals, name='vitals'),
    path('set-csrf-token/', set_csrf_token, name='set-csrf-token'),
    path('get-csrf-token/', get_csrf, name='get-csrf-token'),
    path('validate-move/', validate_move, name='validate-move'),
    path('get-valid-moves/', get_valid_moves, name='get-valid-moves'),
    path('create-room/', create_room, name='create-room'),
    path('join-room/', join_room, name="join-room"),
    path('check-room/<str:roomId>/', check_room, name="check-room"),
    path('check-turn/', check_turn, name="check-turn"),
    path('update-match/', update_match, name="update-match"),
    path('get-fen/', get_fen, name="get-fen"),
    path('check-move-continuation/', check_move_continuation, name="check-move-continuation"),
    path('get-turn/', get_turn, name="get-turn"),
    
    
    

]