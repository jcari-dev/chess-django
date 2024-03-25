import chess

def parse_board(board_dict, turn, castling_rights, en_passant, halfmove_clock, fullmove_number):

    piece_to_fen = {
        "b_rook": "r", "w_rook": "R",
        "b_knight": "n", "w_knight": "N",
        "b_bishop": "b", "w_bishop": "B",
        "b_queen": "q", "w_queen": "Q",
        "b_king": "k", "w_king": "K",
        "b_pawn": "p", "w_pawn": "P",
    }

    fen_rows = []
    for rank in range(8, 0, -1):  # Ranks 8 to 1
        row = ""
        empty_squares = 0
        for file in "abcdefgh":  # Files a to h
            square = f"{file}{rank}"
            if board_dict[square]["piece"]:
                # Convert empty square count to number and reset
                if empty_squares:
                    row += str(empty_squares)
                    empty_squares = 0
                # Append the piece notation
                piece = board_dict[square]["piece"]
                row += piece_to_fen[piece]
            else:
                empty_squares += 1
        # Append remaining empty squares count for the rank
        if empty_squares:
            row += str(empty_squares)
        fen_rows.append(row)

    # Use the turn and fullmove_number parameters in the FEN string
    fen = f"/".join(fen_rows) + \
        f" {turn} {castling_rights} {en_passant} {halfmove_clock} {fullmove_number}"
    return fen

def determine_piece_turn(piece_moving):
    if 'w' == piece_moving[0]:
        return 'w'
    elif 'b' == piece_moving[0]:
        return 'b'
    return False

def get_valid_moves_from_square(fen, file_and_rank):
    
    board = chess.Board(fen)
    
    square = chess.parse_square(file_and_rank)
    
    valid_moves_from_square = [str(move)[2:] for move in board.legal_moves if move.from_square == square]
    
    return valid_moves_from_square
