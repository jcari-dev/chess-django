from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json
import chess
from .utils import parse_board, determine_piece_turn


@require_http_methods(["POST"])
def validate_move(request):
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

        print("---------")

        print(fen_string)

        return JsonResponse({"valid": True})