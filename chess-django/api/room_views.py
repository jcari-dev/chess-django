from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from room.models import Room, Match
import json
import chess
from .utils import determine_piece_turn, parse_board, fen_to_board

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
            room.player_a_color = 'white'
        elif room.player_b is None:
            room.player_b = user_id
            room.player_b_color = 'black'
        else:
            return JsonResponse({'error': 'Room is full.'}, status=400)

        room.save()
        
        if room.player_a and room.player_b:
            if not Match.objects.filter(room=room).exists():
                base_board = chess.Board()
                Match.objects.create(
                    board=base_board.fen(),
                    room=room   
                )

    except Room.DoesNotExist:
        return JsonResponse({'error': 'Room does not exist.'}, status=404)

    return JsonResponse({'message': 'Joined room successfully.'}, status=203)

@require_http_methods(["GET"])
def check_room(request, roomId):
    try:
        room = Room.objects.get(room_id=roomId)
        
        playerA = room.player_a
        playerB = room.player_b

        return JsonResponse({
            'playerA': playerA,
            'playerB': playerB,
            'hasPlayerA': bool(playerA),
            'hasPlayerB': bool(playerB)
        })

    except Room.DoesNotExist:
        return JsonResponse({'error': 'Room does not exist'}, status=404)

@require_http_methods(["POST"])  
def update_match(request):
    data = json.loads(request.body)

    board_data = data['board']

    color_moving = determine_piece_turn(data['pieceMoving'])

    castling_rights = data['castlingRights']

    en_passant = data['enPassant']

    halfmove_clock = data['halfmoveClock']

    fullmove_number = data['turnCount']
    
    room_id = data['roomId']

    fen_string = parse_board(
        board_data, color_moving, castling_rights, en_passant, halfmove_clock, fullmove_number)
    
    print(fen_string, 'before saving')
    
    try:
        room = Room.objects.get(room_id=room_id)
        try:
            match = Match.objects.create(room=room)
            
            match.board = fen_string
            print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
            print(board_data)
            
            new_board_data = fen_to_board(fen_string)
            
            match.save()
            return JsonResponse({'updated': True,
                                 'boardData': new_board_data}, status=203)
        except:
            print('Cant find match to update it.')
            return JsonResponse({'updated': False}, status=404)
            
    except:
        print('Cant find room to update match.')
        return JsonResponse({'updated': False}, status=404)

        
        