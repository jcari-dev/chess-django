

def parse_board(data):
    piece_map = {
    "b_rook": "r", "w_rook": "R",
    "b_knight": "n", "w_knight": "N",
    "b_bishop": "b", "w_bishop": "B",
    "b_queen": "q", "w_queen": "Q",
    "b_king": "k", "w_king": "K",
    "b_pawn": "p", "w_pawn": "P"
}
    
    board = data['board']
    
    for tile in board:
        print(tile, board[tile]['piece'])