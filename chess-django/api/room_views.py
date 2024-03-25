from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from room.models import Room
import json

@require_http_methods(["POST"])
def create_room(request):
    room = Room()
    
    room.save()

    return JsonResponse({
        'message': 'Room created successfully',
        'roomId': room.room_id
    })

@require_http_methods(["POST"])
def join_room(request):
    data = json.loads(request.body)

    print(data)
    user_id = data.get('userId')
    room_id = data.get('roomId')
    
    print(room_id, "room id")

    try:
        room = Room.objects.get(room_id=room_id)
        
        if user_id == room.player_a:
            return JsonResponse({"message": 'Already joined this room.'})
        elif user_id == room.player_b:
            return JsonResponse({"message": 'Already joined this room.'})
        
        if room.player_a is None:
            room.player_a = user_id
        elif room.player_b is None:
            room.player_b = user_id
        else:
            return JsonResponse({'error': 'Room is full.'}, status=400)
        
        room.save()
    except Room.DoesNotExist:
        return JsonResponse({'error': 'Room does not exist.'}, status=404)

    return JsonResponse({'message': 'Joined room successfully.'}, status=203)

def check_room(request, roomId):
    try:
        room = Room.objects.get(room_id=roomId)
        if room.player_b:  # Assuming 'user_b' field becomes non-null when user_b joins
            return JsonResponse({'playerBJoined': True})
        else:
            return JsonResponse({'playerBJoined': False})
    except Room.DoesNotExist:
        return JsonResponse({'error': 'Room does not exist'}, status=404)