import chess
from room.models import Room, Match
import random
from stockfish import Stockfish
from django.core.cache import cache


def parse_board(
    board_dict, turn, castling_rights, en_passant, halfmove_clock, fullmove_number
):

    piece_to_fen = {
        "b_rook": "r",
        "w_rook": "R",
        "b_knight": "n",
        "w_knight": "N",
        "b_bishop": "b",
        "w_bishop": "B",
        "b_queen": "q",
        "w_queen": "Q",
        "b_king": "k",
        "w_king": "K",
        "b_pawn": "p",
        "w_pawn": "P",
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
    fen = (
        f"/".join(fen_rows)
        + f" {turn} {castling_rights} {en_passant} {halfmove_clock} {fullmove_number}"
    )
    return fen


def determine_piece_turn(piece_moving):
    if piece_moving:
        if "w" == piece_moving[0]:
            return "w"
        elif "b" == piece_moving[0]:
            return "b"
        return False


def get_valid_moves_from_square(fen, file_and_rank):

    cached_move_name = f"{fen}{file_and_rank}"
    cached_move = cache.get(cached_move_name)

    if not cached_move:

        board = chess.Board(fen)

        square = chess.parse_square(file_and_rank)

        valid_moves_from_square = [
            str(move)[2:] for move in board.legal_moves if move.from_square == square
        ]
        cache.set(
            cached_move_name, valid_moves_from_square, timeout=28 * 24 * 60 * 60
        )  # 4 weeks of caching

        cached_move = cache.get(cached_move_name)
    else:
        print("Pulling copy from Cache! :)")

    return cached_move


def get_valid_moves_from_square_practice(fen, file_and_rank, difficulty):
    
    cached_move_name = f"{fen}{file_and_rank}{difficulty}"
    cached_valid_moves_from_square_with_scores = cache.get(cached_move_name)

    if not cached_valid_moves_from_square_with_scores:
        board = chess.Board(fen)
        square = chess.parse_square(file_and_rank)
        stockfish = Stockfish("/usr/games/stockfish")

        if difficulty == "Village Hero (Beginner)":
            stockfish.set_skill_level(4)
            stockfish.set_depth(2)

        elif difficulty == "Defender of the Realm (Easy)":
            stockfish.set_skill_level(8)
            stockfish.set_depth(4)

        elif difficulty == "Knight of the Chess Table (Medium)":
            stockfish.set_skill_level(12)
            stockfish.set_depth(6)

        elif difficulty == "Grandmaster Quest (Hard)":
            stockfish.set_skill_level(17)
            stockfish.set_depth(8)

        elif difficulty == "Legend of the Kings (Expert)":
            stockfish.set_skill_level(20)
            stockfish.set_depth(12)

        legal_moves = []
        scores = []
        for move in board.legal_moves:
            if move.from_square == square:
                board_copy = board.copy(stack=False)
                board_copy.push(move)
                stockfish.set_fen_position(board_copy.fen())
                score = stockfish.get_evaluation()["value"]
                legal_moves.append(str(move)[2:])
                scores.append(score)
        valid_moves_from_square_with_scores = {"legal_moves": legal_moves, "scores": scores}
        cache.set(
            cached_move_name, valid_moves_from_square_with_scores, timeout=28 * 24 * 60 * 60
        )  # 4 weeks of caching
        
        cached_valid_moves_from_square_with_scores = cache.get(cached_move_name)
    else:
        print("Pulled move from cache! :)")

    return cached_valid_moves_from_square_with_scores


def determine_online_turn(fen):

    board = chess.Board(fen)

    return not board.turn


def fen_to_board(fen):
    piece_to_full = {
        "r": "b_rook",
        "n": "b_knight",
        "b": "b_bishop",
        "q": "b_queen",
        "k": "b_king",
        "p": "b_pawn",
        "R": "w_rook",
        "N": "w_knight",
        "B": "w_bishop",
        "Q": "w_queen",
        "K": "w_king",
        "P": "w_pawn",
    }

    # Initialize the board object
    board = {}
    rank = 8  # Start from the top of the board
    file = "a"  # Start from the left of the board
    files = "abcdefgh"

    # Helper to get square color
    def get_square_color(file, rank):
        # Files 'a', 'c', 'e', 'g' are 'white' on even ranks and 'coral' on odd ranks
        if file in "aceg":
            return "coral" if rank % 2 == 0 else "white"
        else:
            return "white" if rank % 2 == 0 else "coral"

    # Process the board part of the FEN string
    for char in fen.split(" ")[0]:
        if char == "/":  # Move down a rank
            rank -= 1
            file = "a"
        elif char.isdigit():  # Empty squares
            for _ in range(int(char)):
                square = f"{file}{rank}"
                color = get_square_color(file, rank)
                board[square] = {"piece": "", "color": color, "highlight": False}
                file = files[(files.index(file) + 1) % 8]
        else:  # Piece symbols
            square = f"{file}{rank}"
            color = get_square_color(file, rank)
            board[square] = {
                "piece": piece_to_full[char],
                "color": color,
                "highlight": False,
            }
            file = files[(files.index(file) + 1) % 8]

    return board


def is_valid_fen(fen_str):
    try:
        chess.Board(fen_str)
        return True
    except ValueError:
        return False


def get_turn_count(room_id):

    try:
        room = Room.objects.get(room_id=room_id)
        try:

            match_data = Match.objects.filter(room=room).latest(
                "id"
            )  # Efficiently fetch the latest match

            return int(match_data.board.split(" ")[-1])

        except:
            print("Cant find match data. To determine turn.")
    except:
        print("Cant find room. To determine turn.")


def sort_colors(user_color):
    color_choices = ["white", "black"]

    if user_color == "white":
        cpu_color = "black"
    elif user_color == "black":
        cpu_color = "white"
    elif user_color == "random":
        # Randomly select for user, ensuring CPU gets the opposite color
        user_color = random.choice(color_choices)
        cpu_color = "black" if user_color == "white" else "white"
    else:
        # If somehow the color isnt white, black or random
        cpu_color = "unknown"

    return {"user_color": user_color, "cpu_color": cpu_color}


def stockfish_move(difficulty, fen):
    stockfish = Stockfish("/usr/games/stockfish")

    # Set the board position using the FEN
    stockfish.set_fen_position(fen)

    if difficulty == "Village Hero (Beginner)":
        stockfish.set_skill_level(4)
        stockfish.set_depth(2)
        best_move = stockfish.get_best_move_time(100)  # Time is in milliseconds
    elif difficulty == "Defender of the Realm (Easy)":
        stockfish.set_skill_level(8)
        stockfish.set_depth(4)
        best_move = stockfish.get_best_move_time(200)
    elif difficulty == "Knight of the Chess Table (Medium)":
        stockfish.set_skill_level(12)
        stockfish.set_depth(6)
        best_move = stockfish.get_best_move_time(500)
    elif difficulty == "Grandmaster Quest (Hard)":
        stockfish.set_skill_level(17)
        stockfish.set_depth(8)
        best_move = stockfish.get_best_move_time(1000)
    elif difficulty == "Legend of the Kings (Expert)":
        stockfish.set_skill_level(20)
        stockfish.set_depth(12)
        best_move = stockfish.get_best_move_time(2000)
    else:
        print(difficulty)
        raise ValueError("Unsupported difficulty level")

    best_move = stockfish.get_best_move()

    # Apply best move to the current board
    stockfish.make_moves_from_current_position([best_move])

    # Get the fen from that board.

    new_fen = stockfish.get_fen_position()

    print(new_fen, "This is what stockfish thinks is the best move now.")

    return new_fen