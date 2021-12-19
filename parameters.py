SCREEN_WIGHT, SCREEN_HEIGHT = 1500, 750
WINDOW_TITLE = "Domino"
BACKGROUND_COLOR = [(207, 235, 199), (139, 159, 104)]

DOMINO_CELL_SIZE = 30
DOMINO_COLOR = (255, 255, 255)
DOMINO_DOT_COLOR = (0, 0, 0)
DOMINO_INTERVAL = DOMINO_CELL_SIZE + 5

BORDER_COLOR = (0, 0, 0)

TRANSPARENT_COLOR = (255, 0, 0)

STORAGE_COORDS = (660, 330)

THIRD_COLOR = (86, 113, 131)

PLAYER1 = 'player1'
PLAYER2 = 'player2'

PLAYERS_COLORS = {
    PLAYER1: (237, 145, 226),
    PLAYER2: (250, 187, 136)
}

# Режимы игры
PLAYER1_MOVE = 1       # Ход игрока
PLAYER2_MOVE = 2       # Ход компьютера
END_GAME = 3           # Игра окончена

# Окончания игры
PLAYER1_WIN = 1             # Игрок победил
PLAYER2_WIN = 2             # Компьютер победил
STANDOFF = 3                # Ничья