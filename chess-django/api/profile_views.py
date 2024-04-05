from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from room.models import Room
from django.db.models import Q
from django_ratelimit.decorators import ratelimit

import json


@ratelimit(key="ip", rate="5/s", block=True)
@require_http_methods(["POST"])
def get_profile(request):
    data = json.loads(request.body)

    user_id = data.get("userId")

    matches = Room.objects.filter(Q(player_a=user_id) | Q(player_b=user_id)).order_by(
        "-id"
    )

    matches_data = list(matches.values())
    # print(matches_data)

    return JsonResponse({"matches": matches_data})
