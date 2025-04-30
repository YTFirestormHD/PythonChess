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


# Piece class
class Piece:
    def __init__(self, color, piece_type):
        self.color = color
        self.piece_type = piece_type
        self.image = pygame.image.load(f"../assets/{piece_type}_{color}.png")

    def __repr__(self):
        return f"{self.color} {self.piece_type}"


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


# Set up the display with resizable flag
screen = pygame.display.set_mode((BOARD_SIZE, BOARD_SIZE), pygame.RESIZABLE)
pygame.display.set_caption("Schach")

# Create board
board = Board()


def draw_board(screen_width, screen_height):
    # Calculate the size of the board to fit the window
    board_size = min(screen_width, screen_height)
    square_size = board_size // 8

    # Calculate offsets to center the board
    x_offset = (screen_width - board_size) // 2
    y_offset = (screen_height - board_size) // 2

    # Draw squares
    for row in range(8):
        for col in range(8):
            color = LIGHT_BROWN if (row + col) % 2 == 0 else DARK_BROWN
            pygame.draw.rect(screen, color,
                             (x_offset + col * square_size, y_offset + row * square_size, square_size, square_size))

    # Draw pieces
    for row in range(8):
        for col in range(8):
            piece = board.board[row][col]
            if piece:
                # Scale piece image to current square size
                scaled_image = pygame.transform.scale(piece.image, (square_size, square_size))
                screen.blit(scaled_image, (x_offset + col * square_size, y_offset + row * square_size))

                


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
            # Update screen with new size
            global screen
            screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

    # Get current window size
    screen_width, screen_height = screen.get_size()

    # Clear screen and draw board with pieces
    screen.fill(WHITE)
    draw_board(screen_width, screen_height)
    pygame.display.flip()


async def main():
    setup()
    while True:
        update_loop()
        await asyncio.sleep(1.0 / FPS)


if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())
