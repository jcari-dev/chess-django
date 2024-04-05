from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from room.models import Room, Match
from django.db.models import Q
from django_ratelimit.decorators import ratelimit

import json


@ratelimit(key="ip", rate="5/s", block=True)
@require_http_methods(["POST"])
def get_profile(request):
    data = json.loads(request.body)
    user_id = data.get("userId")

    rooms = Room.objects.filter(Q(player_a=user_id) | Q(player_b=user_id)).order_by(
        "-id"
    )

    matches_data = []

    for room in rooms:
        latest_match = Match.objects.filter(room=room).order_by("-id").first()

        room_dict = {
            "room_id": room.room_id,
            "status": room.status,
            "player_a": room.player_a,
            "player_b": room.player_b,
            "player_a_color": room.player_a_color,
            "player_b_color": room.player_b_color,
            "winner": room.winner,
            "last_played": room.last_played,
            "turns": latest_match.board.split(" ")[-1] if latest_match else None,
        }

        matches_data.append(room_dict)

    return JsonResponse({"matches": matches_data})
