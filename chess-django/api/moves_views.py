from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json
import chess
from .utils import fen_to_board, parse_board, determine_piece_turn, get_valid_moves_from_square
from room.models import Match, Room
from pprint import pprint

@require_http_methods(["POST"])
def get_valid_moves(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        board_data = data['board']

        color_moving = determine_piece_turn(data['pieceMoving'])

        castling_rights = data['castlingRights']

        en_passant = data['enPassant']

        halfmove_clock = data['halfmoveClock']

        fullmove_number = data['turnCount']

        fen_string = parse_board(
            board_data, color_moving, castling_rights, en_passant, halfmove_clock, fullmove_number)

        legal_moves = get_valid_moves_from_square(fen_string, data['target'])
        print("Legal moves generated: ", legal_moves)
        return JsonResponse({"legalMoves": legal_moves})


@require_http_methods(["POST"])
def check_turn(request):
    data = json.loads(request.body)
    room_id = data['roomId']
    requester_id = data['userId']

    try:
        room = Room.objects.get(room_id=room_id)
        match_data = Match.objects.filter(room=room).latest('id')

        if requester_id == room.player_a:
            requester_color = room.player_a_color
        elif requester_id == room.player_b:
            requester_color = room.player_b_color
        else:
            return JsonResponse({"error": "Requester is not a player in this room."}, status=400)

        fen = match_data.board

        boardData = fen_to_board(fen)
        board = chess.Board(fen)
        my_turn = False
        color = ""
        turn_count = int(match_data.board.split(" ")[-1])
        if board.turn and requester_color == "white":
            my_turn = True
            color = "w"

        elif not board.turn and requester_color == "black":
            my_turn = True
            color = "b"
    
        return JsonResponse({"myTurn": my_turn, "color": color, "boardData": boardData, "turnCount": turn_count})

    except Room.DoesNotExist:
        return JsonResponse({"error": "Room does not exist."}, status=404)
    except Exception as e:
        print(f"Error: {e}")
        return JsonResponse({"error": "An unexpected error occurred."}, status=500)


@require_http_methods(["POST"])
def check_move_continuation(request):
    try:

        data = json.loads(request.body)

        room_id = data['roomId']

        board_data = data['board']
        
        pprint(board_data)

        color_moving = determine_piece_turn(data['pieceMoving']) # In this case it will always be inverted

        castling_rights = data['castlingRights']

        en_passant = data['enPassant']

        halfmove_clock = data['halfmoveClock']

        fullmove_number = data['turnCount']

        target_fen = parse_board(
            board_data, color_moving, castling_rights, en_passant, halfmove_clock, fullmove_number)
        
        print(target_fen, "This is the target fen.")

        try:
            room = Room.objects.get(room_id=room_id)
            match_data = Match.objects.filter(room=room).latest('id')
            print(match_data.board, 'This is the latest on the database.')

            initial_fen = match_data.board

            board = chess.Board(initial_fen)

            def is_valid_continuation(board, target_fen):
                
                for move in board.legal_moves:
                    board.push(move)
                    print("Valid moves: ", board.fen(), "My fen: ", target_fen)
                    if board.fen() == target_fen:
                        return True
                    board.pop()
                return False

            valid_continuation = is_valid_continuation(board, target_fen)
            
            if valid_continuation:
                updated_match = Match.objects.create(room=room, board=target_fen)
                updated_match.save()
            else:
                print('Invalid FEN.')

            return JsonResponse({"valid_continuation": valid_continuation})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
