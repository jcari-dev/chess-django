from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json
import chess
from .utils import parse_board, determine_piece_turn, get_valid_moves_from_square
from room.models import Match, Room


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
    if request.method == 'POST':
        data = json.loads(request.body)

        room_id = data['roomId']
        requester_id = data['userId']
        
        try:
            room = Room.objects.get(room_id=room_id)
        except:
            print("Unable to fetch room data.")
        
        print(room_id, requester_id, "checking turn data")
        
        try:
            
            print('trying to find match data ):')
            
            match_data = Match.objects.filter(room=room).order_by("-id")[0]
            
            print(match_data, "FOUND MATCH DATA")
            
            room_data = match_data.room
            
            match_fen = match_data.board
            
            turn_according_to_db = match_fen.split()[1] # b or w
            
            if requester_id == room_data.player_a:
                if turn_according_to_db == room_data.player_a_color[0]:
                    my_turn = True
                else:
                    my_turn = False
            elif requester_id == room_data.player_b:
                if turn_according_to_db == room_data.player_b_color[0]:
                    my_turn = True
                else:
                    my_turn = False
            # print('hi?', requester_id)
            return JsonResponse({"myTurn": my_turn})

        except Exception as e:
            print(f'Unable to fetch match data: {e}')
        
        return JsonResponse({"invalid": True})