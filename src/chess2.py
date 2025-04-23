import asyncio
import platform
import pygame

# Initialize Pygame
pygame.init()

# Constants
SQUARE_SIZE = 60
BOARD_SIZE = 8 * SQUARE_SIZE
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_BROWN = (240, 217, 181)
DARK_BROWN = (181, 136, 99)
HIGHLIGHT = (100, 255, 100, 128)  # Semi-transparent green for highlights
SELECTED = (255, 255, 0)  # Yellow for selected piece border.

# Set up the display with resizable flag
screen = pygame.display.set_mode((BOARD_SIZE, BOARD_SIZE), pygame.RESIZABLE)
pygame.display.set_caption("Schach")

# Piece class
class Piece:
    def __init__(self, color, piece_type):
        self.color = color
        self.piece_type = piece_type
        self.image = pygame.image.load(f"../assets/{piece_type}_{color}.png")

    def __repr__(self):
        return f"{self.color} {self.piece_type}"

    def get_valid_moves(self, board, row, col):
        """Return a list of valid move positions (row, col) for the piece."""
        moves = []
        if self.piece_type == "Pawn":
            direction = -1 if self.color == "White" else 1
            start_row = 6 if self.color == "White" else 1
            # Move forward
            if 0 <= row + direction < 8 and board[row + direction][col] is None:
                moves.append((row + direction, col))
                # Double move from starting position
                if row == start_row and board[row + 2 * direction][col] is None:
                    moves.append((row + 2 * direction, col))
            # Capture diagonally
            for dc in [-1, 1]:
                if 0 <= row + direction < 8 and 0 <= col + dc < 8:
                    if board[row + direction][col + dc] and board[row + direction][col + dc].color != self.color:
                        moves.append((row + direction, col + dc))
        elif self.piece_type == "Rook":
            for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                r, c = row, col
                while True:
                    r, c = r + dr, c + dc
                    if not (0 <= r < 8 and 0 <= c < 8):
                        break
                    if board[r][c] is None:
                        moves.append((r, c))
                    elif board[r][c].color != self.color:
                        moves.append((r, c))
                        break
                    else:
                        break
        elif self.piece_type == "Knight":
            for dr, dc in [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]:
                r, c = row + dr, col + dc
                if 0 <= r < 8 and 0 <= c < 8:
                    if board[r][c] is None or board[r][c].color != self.color:
                        moves.append((r, c))
        elif self.piece_type == "Bishop":
            for dr, dc in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
                r, c = row, col
                while True:
                    r, c = r + dr, c + dc
                    if not (0 <= r < 8 and 0 <= c < 8):
                        break
                    if board[r][c] is None:
                        moves.append((r, c))
                    elif board[r][c].color != self.color:
                        moves.append((r, c))
                        break
                    else:
                        break
        elif self.piece_type == "Queen":
            for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
                r, c = row, col
                while True:
                    r, c = r + dr, c + dc
                    if not (0 <= r < 8 and 0 <= c < 8):
                        break
                    if board[r][c] is None:
                        moves.append((r, c))
                    elif board[r][c].color != self.color:
                        moves.append((r, c))
                        break
                    else:
                        break
        elif self.piece_type == "King":
            for dr, dc in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
                r, c = row + dr, col + dc
                if 0 <= r < 8 and 0 <= c < 8:
                    if board[r][c] is None or board[r][c].color != self.color:
                        moves.append((r, c))
        return moves

# Board class
class Board:
    def __init__(self):
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.setup_board()

    def setup_board(self):
        # Place pawns
        for col in range(8):
            self.board[1][col] = Piece("Black", "Pawn")
            self.board[6][col] = Piece("White", "Pawn")
        # Place other pieces
        self.board[0][0] = self.board[0][7] = Piece("Black", "Rook")
        self.board[0][1] = self.board[0][6] = Piece("Black", "Knight")
        self.board[0][2] = self.board[0][5] = Piece("Black", "Bishop")
        self.board[0][3] = Piece("Black", "Queen")
        self.board[0][4] = Piece("Black", "King")
        self.board[7][0] = self.board[7][7] = Piece("White", "Rook")
        self.board[7][1] = self.board[7][6] = Piece("White", "Knight")
        self.board[7][2] = self.board[7][5] = Piece("White", "Bishop")
        self.board[7][3] = Piece("White", "Queen")
        self.board[7][4] = Piece("White", "King")

    def move_piece(self, from_pos, to_pos):
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        self.board[to_row][to_col] = self.board[from_row][from_col]
        self.board[from_row][from_col] = None

# Game state
class Game:
    def __init__(self):
        self.board = Board()
        self.current_turn = "White"
        self.selected_piece = None
        self.selected_pos = None
        self.valid_moves = []

    def switch_turn(self):
        self.current_turn = "Black" if self.current_turn == "White" else "White"
        self.selected_piece = None
        self.selected_pos = None
        self.valid_moves = []

    def handle_click(self, pos, square_size, x_offset, y_offset):
        # Convert pixel position to board coordinates
        col = (pos[0] - x_offset) // square_size
        row = (pos[1] - y_offset) // square_size
        if not (0 <= row < 8 and 0 <= col < 8):
            return

        if self.selected_piece is None:
            # Select a piece
            piece = self.board.board[row][col]
            if piece and piece.color == self.current_turn:
                self.selected_piece = piece
                self.selected_pos = (row, col)
                self.valid_moves = piece.get_valid_moves(self.board.board, row, col)
        else:
            # Try to move the selected piece.
            if (row, col) in self.valid_moves:
                self.board.move_piece(self.selected_pos, (row, col))
                self.switch_turn()
            else:
                # Deselect if clicking an invalid move
                self.selected_piece = None
                self.selected_pos = None
                self.valid_moves = []

# Create game
game = Game()

def draw_board(screen_width, screen_height):
    # Calculate board size and square size
    board_size = min(screen_width, screen_height)
    square_size = board_size // 8
    x_offset = (screen_width - board_size) // 2
    y_offset = (screen_height - board_size) // 2

    # Draw squares
    for row in range(8):
        for col in range(8):
            color = LIGHT_BROWN if (row + col) % 2 == 0 else DARK_BROWN
            pygame.draw.rect(screen, color, (x_offset + col * square_size, y_offset + row * square_size, square_size, square_size))

    # Draw valid move highlights
    if game.valid_moves:
        highlight_surface = pygame.Surface((square_size, square_size), pygame.SRCALPHA)
        highlight_surface.fill(HIGHLIGHT)
        for move in game.valid_moves:
            row, col = move
            screen.blit(highlight_surface, (x_offset + col * square_size, y_offset + row * square_size))

    # Draw pieces
    for row in range(8):
        for col in range(8):
            piece = game.board.board[row][col]
            if piece:
                scaled_image = pygame.transform.scale(piece.image, (square_size, square_size))
                screen.blit(scaled_image, (x_offset + col * square_size, y_offset + row * square_size))

    # Draw selected piece border
    if game.selected_pos:
        row, col = game.selected_pos
        pygame.draw.rect(screen, SELECTED, (x_offset + col * square_size, y_offset + row * square_size, square_size, square_size), 3)

    # Draw labels (A-H and 1-8)
    font = pygame.font.SysFont("arial", square_size // 3)
    for i in range(8):
        # Letters (A-H) top and bottom
        letter = chr(65 + i)  # A=65 in ASCII
        label = font.render(letter, True, BLACK)
        label_rect = label.get_rect()
        label_rect.center = (x_offset + i * square_size + square_size // 2, y_offset - square_size // 4)
        screen.blit(label, label_rect)
        label_rect.center = (x_offset + i * square_size + square_size // 2, y_offset + board_size + square_size // 4)
        screen.blit(label, label_rect)
        # Numbers (1-8) left and right
        number = str(8 - i)
        label = font.render(number, True, BLACK)
        label_rect = label.get_rect()
        label_rect.center = (x_offset - square_size // 4, y_offset + i * square_size + square_size // 2)
        screen.blit(label, label_rect)
        label_rect.center = (x_offset + board_size + square_size // 4, y_offset + i * square_size + square_size // 2)
        screen.blit(label, label_rect)

def setup():
    screen.fill(WHITE)
    draw_board(BOARD_SIZE, BOARD_SIZE)
    pygame.display.flip()

def update_loop():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            return
        elif event.type == pygame.VIDEORESIZE:
            global screen
            screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Calculate board parameters for click handling
            screen_width, screen_height = screen.get_size()
            board_size = min(screen_width, screen_height)
            square_size = board_size // 8
            x_offset = (screen_width - board_size) // 2
            y_offset = (screen_height - board_size) // 2
            game.handle_click(event.pos, square_size, x_offset, y_offset)

    # Draw board and pieces
    screen_width, screen_height = screen.get_size()
    screen.fill(WHITE)
    draw_board(screen_width, screen_height)
    pygame.display.flip()

async def main():
    setup()
    while True:
        update_loop()
        await asyncio.sleep(1.0 / FPS)

if __name__ == "__main__":
    asyncio.run(main())
