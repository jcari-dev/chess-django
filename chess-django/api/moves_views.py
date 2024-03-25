from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json
import chess
from .utils import parse_board, determine_piece_turn, get_valid_moves_from_square


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