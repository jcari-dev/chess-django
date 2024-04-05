from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from room.models import Room, Match
import json
import chess
from django_ratelimit.decorators import ratelimit
from .utils import (
    determine_piece_turn,
    get_turn_count,
    parse_board,
    fen_to_board,
    is_valid_fen,
    sort_colors,
    stockfish_move,
)


@ratelimit(key="ip", rate="3/s", block=True)
@require_http_methods(["POST"])
def create_cpu_room(request):
    data = json.loads(request.body)

    difficulty = data["difficulty"]
    print(difficulty, "CREATING ROOM")
    color = data["color"]
    user_id = data["userId"]
    practice = data["practiceMode"]

    colors = sort_colors(color)

    room = Room()
    room.player_a = user_id
    room.player_b = f"Stockfish - {difficulty}"
    room.player_a_color = colors["user_color"]
    room.player_b_color = colors["cpu_color"]

    room.save()

    base_board = chess.Board()
    match = Match(board=base_board.fen(), room=room, difficulty=difficulty, practice=practice)
    # Here you can manipulate or check the match object as needed before saving
    match.save()

    print(match.id, match.difficulty, "MATCH ID")

    return JsonResponse({"room": room.room_id})

    
@ratelimit(key="ip", rate="5/s", block=True)
@require_http_methods(["POST"])
def check_turn_cpu(request):
    data = json.loads(request.body)
    room_id = data["roomId"]
    requester_id = data["userId"]

    try:
        room = Room.objects.get(room_id=room_id)

        match_data = Match.objects.filter(room=room).latest("id")

        fen = match_data.board

        boardData = fen_to_board(match_data.board)
        
        if room.winner and room.winner != "Unknown":
            boardData = fen_to_board(fen)

            return JsonResponse(
                {"winner": room.winner, "boardData": boardData}, status=200
            )

        requester_color = room.player_a_color

        board = chess.Board(fen)

        is_in_check = board.is_check()

        is_checkmate = board.is_checkmate()

        if is_checkmate:
            room.status = "FINISHED"
            winner = "white" if board.turn == chess.BLACK else "black"
            room.winner = winner
            room.save()

        my_turn = False
        
        color = ""

        if board.turn and requester_color == "white":
            my_turn = True
            print("????? white turn")
            color = "w"

        elif not board.turn and requester_color == "black":
            print("????? black turn")
            my_turn = True
            color = "b"
            
        turn_count = int(match_data.board.split(" ")[-1])
        halfmove_clock = int(match_data.board.split(" ")[-2])
        
        if not my_turn:
            difficulty = match_data.difficulty
            stockfish_fen_response = stockfish_move(match_data.difficulty, fen)
            boardData = fen_to_board(stockfish_fen_response)
            turn_count = int(stockfish_fen_response.split(" ")[-1])
            halfmove_clock = int(stockfish_fen_response.split(" ")[-2])
            board = chess.Board(stockfish_fen_response)
            is_in_check = board.is_check()
            updated_match = Match.objects.create(room=room, board=stockfish_fen_response, difficulty=difficulty)
            updated_match.save()
            is_checkmate = board.is_checkmate()
            my_turn = True
            print("?@@@???@?@??")
            if requester_color == "black":
                color = "b"
            elif requester_color == "white":
                color = "w"
            

        return JsonResponse(
            {
                "myTurn": my_turn,
                "color": color,
                "boardData": boardData,
                "turnCount": turn_count,
                "halfmoveClock": halfmove_clock,
                "check": is_in_check,
                "checkmate": is_checkmate,
            }
        )

    except Room.DoesNotExist:
        return JsonResponse({"error": "Room does not exist."}, status=404)
    except Exception as e:
        print(f"Error: {e}")
        return JsonResponse({"error": "An unexpected error occurred."}, status=500)
