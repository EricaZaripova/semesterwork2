import pygame

from parameters import BACKGROUND_COLOR, SCREEN_WIGHT, SCREEN_HEIGHT, DOMINO_CELL_SIZE, BORDER_COLOR, \
    WIN, STANDOFF, THIRD_COLOR, TRANSPARENT_COLOR, DOMINO_INTERVAL, STORAGE_COORDS


def get_player_pool_position(player_pool):
    return SCREEN_WIGHT // 2 - player_pool.PANE_WIDTH // 2, player_pool.PANE_HEIGHT - 3 * DOMINO_CELL_SIZE


def get_domino_backside():
    surface = pygame.Surface((DOMINO_CELL_SIZE, 2 * DOMINO_CELL_SIZE))
    surface.fill(THIRD_COLOR)
    pygame.draw.rect(surface, BORDER_COLOR, (0, 0, DOMINO_CELL_SIZE, 2 * DOMINO_CELL_SIZE), 1)

    return surface


def get_storage():
    surface = pygame.Surface((4 * DOMINO_CELL_SIZE, 2 * DOMINO_CELL_SIZE))
    surface.fill(THIRD_COLOR)
    pygame.draw.rect(surface, BORDER_COLOR, (0, 0, 4 * DOMINO_CELL_SIZE, 2 * DOMINO_CELL_SIZE), 1)

    return surface


def check_available_for_domino(domino, chain):
    available_for_left = domino.side1 == chain.left_side or domino.side2 == chain.left_side
    available_for_right = domino.side1 == chain.right_side or domino.side2 == chain.right_side
    return available_for_left, available_for_right


def check_end_game(player_pool, opponent_pool, storage):
    if player_pool.is_empty:
        return WIN

    if storage == 0 and not is_available_moves(player_pool) and opponent_pool:
        return STANDOFF

    return None


def is_available_moves(pool):
    for domino in pool.domino_list:
        available_for_left, available_for_right = check_available_for_domino(domino, pool.chain)
        if available_for_left or available_for_right:
            return True
    return False


def storage_click(pos):
    domino_rect = pygame.Rect(STORAGE_COORDS[0], STORAGE_COORDS[1], 4 * DOMINO_CELL_SIZE, 2 * DOMINO_CELL_SIZE)
    if domino_rect.collidepoint(pos[0], pos[1]):
        return True
    return False


def draw_background(surface):
    pygame.draw.rect(surface, BACKGROUND_COLOR[1], (0, 0, SCREEN_WIGHT, 120))
    pygame.draw.rect(surface, BACKGROUND_COLOR[0], (0, 120, SCREEN_WIGHT, 630))
    pygame.draw.rect(surface, BACKGROUND_COLOR[1], (0, 630, SCREEN_WIGHT, SCREEN_HEIGHT))


def draw_waiting_pane(surface):
    x1, y1 = SCREEN_WIGHT // 2 - DOMINO_CELL_SIZE * 6, SCREEN_HEIGHT // 2 - DOMINO_CELL_SIZE * 2
    pygame.draw.rect(surface, THIRD_COLOR, (x1, y1, DOMINO_CELL_SIZE * 12, DOMINO_CELL_SIZE * 4))

    font_result = pygame.font.Font(None, 42)
    text = font_result.render('Waiting for Opponent...', True, BORDER_COLOR)
    surface.blit(text, (SCREEN_WIGHT / 2 - text.get_width() / 2, SCREEN_HEIGHT / 2 - text.get_height() / 2))


def draw_chain(surface, chain):
    chain.create_surface()
    surface.blit(chain.surface, (0, 0))


def draw_storage_pane(surface, number):
    storage_surface = pygame.Surface((SCREEN_WIGHT, SCREEN_HEIGHT))
    storage_surface.set_colorkey(TRANSPARENT_COLOR)
    storage_surface.fill(TRANSPARENT_COLOR)
    if not number:
        return

    backside_surface = get_storage()
    storage_surface.blit(backside_surface, STORAGE_COORDS)

    font = pygame.font.Font(None, 80)
    font_surface = font.render(str(number), True, BORDER_COLOR)
    font_rect = font_surface.get_rect()

    storage_surface.blit(font_surface,
                         (SCREEN_WIGHT // 2 - font_rect.width, SCREEN_HEIGHT // 2 - 0.75 * font_rect.height))

    surface.blit(storage_surface, (0, 0))


def draw_restart_button(surface, button):
    button.create_surface()
    surface.blit(button.surface, (0, 0))


def draw_player_pool(surface, player1_pool, chain, turn):
    player1_pool.create_surface(chain, turn)
    x, y = get_player_pool_position(player1_pool)
    surface.blit(player1_pool.surface, (x, y))


def draw_opponent_pool(surface, opponent_pool):
    PANE_WIDTH = SCREEN_WIGHT
    PANE_HEIGHT = 3 * DOMINO_CELL_SIZE

    surface_pool = pygame.Surface((PANE_WIDTH, PANE_HEIGHT))
    surface_pool.set_colorkey(TRANSPARENT_COLOR)
    surface_pool.fill(TRANSPARENT_COLOR)
    domino_block_width = DOMINO_INTERVAL * opponent_pool
    block_x0, block_y0 = PANE_WIDTH // 2 - domino_block_width // 2, DOMINO_CELL_SIZE
    domino_backside = get_domino_backside()
    for index in range(opponent_pool):
        surface_pool.blit(domino_backside, (block_x0 + index * DOMINO_INTERVAL, block_y0))
    surface.blit(surface_pool, (0, 0))


def draw_game_result(surface, game_result):
    surface.blit(game_result.surface, (0, 0))


def is_quit_event(events):
    for event in events:
        if event.type == pygame.QUIT:
            return True
    return False

