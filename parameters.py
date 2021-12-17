SCREEN_WIGHT, SCREEN_HEIGHT = 1500, 750
WINDOW_TITLE = "Domino"
BACKGROUND_COLOR = [(94, 99, 182), (163, 147, 235)]

DOMINO_CELL_SIZE = 30
DOMINO_COLOR = (255, 255, 255)
DOMINO_DOT_COLOR = (0, 0, 0)
DOMINO_BACK_COLOR = (161, 161, 161)
DOMINO_INTERVAL = DOMINO_CELL_SIZE + 5

BORDER_COLOR = (0, 0, 0)

TRANSPARENT_COLOR = (255, 0, 0)

STORAGE_COORDS = (720, 360)

RESULT_BACKGROUND_COLOR = (245, 199, 247)

PLAYER1 = 'player1'
PLAYER2 = 'player2'

PLAYERS_COLORS = {
    PLAYER1: (0, 250, 0),
    PLAYER2: (250, 0, 0)
}

# Режимы игры
PLAYER1_MOVE = 1       # Ход игрока
PLAYER2_MOVE = 2       # Ход компьютера
END_GAME = 3           # Игра окончена

# Окончания игры
PLAYER1_WIN = 1             # Игрок победил
PLAYER2_WIN = 2             # Компьютер победил
STANDOFF = 3                # Ничья
