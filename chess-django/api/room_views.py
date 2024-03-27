from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from room.models import Room, Match
import json
import chess
from .utils import determine_piece_turn, get_turn_count, parse_board, fen_to_board, is_valid_fen


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

    # Extract data from request
    board_data = data['board']
    print(data['pieceMoving'])
    color_moving = determine_piece_turn(data['pieceMoving'])
    print(color_moving)
    castling_rights = data['castlingRights']
    en_passant = data['enPassant']
    halfmove_clock = data['halfmoveClock']
    fullmove_number = data['turnCount']
    room_id = data['roomId']

    # Generate FEN string from the provided data
    fen_string = parse_board(board_data, color_moving, castling_rights,
                             en_passant, halfmove_clock, fullmove_number)
    print(fen_string, "Fen string of current game state")
    if not is_valid_fen(fen_string):
        print('invalid fen')
        return JsonResponse({"error": "Invalid FEN"}, status=400)

    try:
        room = Room.objects.get(room_id=room_id)

        # Fetch the latest match for the room, if any
        latest_match = Match.objects.filter(room=room).order_by('-id').first()

        if latest_match:
            # Parse the fullmove number from the latest match's FEN
            existing_fullmove_number = int(latest_match.board.split(' ')[-1])

            print(existing_fullmove_number,
                  "This is currently the number in the database for this match")
            print(fullmove_number, "This is the one currently being saved.")

            # If incoming turn count is lower, do not update
            if fullmove_number <= existing_fullmove_number:
                return JsonResponse({'error': 'Incoming turn count is lower than the existing one.'}, status=409)

        # Proceed to create or update the match
        match = Match.objects.create(
            room=room, board=fen_string) if not latest_match else latest_match
        match.board = fen_string  # Update the board with the new FEN
        match.save()  # Save the match with the updated details

        # Assuming this is a valid function to convert FEN to board data
        new_board_data = fen_to_board(fen_string)

        return JsonResponse({'updated': True, 'boardData': new_board_data}, status=203)

    except Room.DoesNotExist:
        return JsonResponse({'error': 'Cannot find room to update match.'}, status=404)
    except Exception as e:
        print(f'Error: {e}')
        return JsonResponse({'error': 'An unexpected error occurred.'}, status=500)


@require_http_methods(["POST"])
def get_fen(request):
    data = json.loads(request.body)

    room_id = data.get('roomId')

    try:
        room = Room.objects.get(room_id=room_id)

        match_data = Match.objects.filter(room=room).latest(
            'id')  # Efficiently fetch the latest match

        return JsonResponse({"fen": match_data.board})

    except Room.DoesNotExist:
        return JsonResponse({'error': 'Room does not exist.'}, status=404)

    return JsonResponse({'message': 'Joined room successfully.'}, status=203)


@require_http_methods(["POST"])
def get_turn(request):
    data = json.loads(request.body)

    room_id = data.get('roomId')

    try:
        return JsonResponse({"turn":  get_turn_count(room_id)})

    except:
        return JsonResponse({'error': 'Getting the turn count.'}, status=400)
