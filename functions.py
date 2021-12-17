import pygame

from parameters import BACKGROUND_COLOR, SCREEN_WIGHT, SCREEN_HEIGHT, DOMINO_CELL_SIZE, DOMINO_BACK_COLOR, BORDER_COLOR, \
    PLAYER1_WIN, PLAYER2_WIN, STANDOFF


def get_player_pool_position(player_pool):
    return SCREEN_WIGHT // 2 - player_pool.PANE_WIDTH // 2, player_pool.PANE_HEIGHT - 3 * DOMINO_CELL_SIZE


def get_domino_backside():
    surface = pygame.Surface((DOMINO_CELL_SIZE, 2 * DOMINO_CELL_SIZE))
    surface.fill(DOMINO_BACK_COLOR)
    pygame.draw.rect(surface, BORDER_COLOR, (0, 0, DOMINO_CELL_SIZE, 2 * DOMINO_CELL_SIZE), 1)

    return surface


def get_storage():
    surface = pygame.Surface((2 * DOMINO_CELL_SIZE, DOMINO_CELL_SIZE))
    surface.fill(DOMINO_BACK_COLOR)
    pygame.draw.rect(surface, BORDER_COLOR, (0, 0, 2 * DOMINO_CELL_SIZE, DOMINO_CELL_SIZE), 1)

    return surface


def check_available_for_domino(domino, chain):
    available_for_left = domino.side1 == chain.left_side or domino.side2 == chain.left_side
    available_for_right = domino.side1 == chain.right_side or domino.side2 == chain.right_side
    return available_for_left, available_for_right


def check_end_game(player1_pool, player2_pool, storage):
    if player1_pool.is_empty:
        return PLAYER1_WIN
    if player2_pool.is_empty:
        return PLAYER2_WIN

    if storage.is_empty and not is_available_moves(player1_pool) and not is_available_moves(player2_pool):
        return STANDOFF

    return None


def is_available_moves(pool):
    for domino in pool.domino_list:
        available_for_left, available_for_right = check_available_for_domino(domino, pool.chain)
        if available_for_left or available_for_right:
            return True
    return False


def draw_background(surface):
    pygame.draw.rect(surface, BACKGROUND_COLOR[1], (0, 0, SCREEN_WIGHT, 120))
    pygame.draw.rect(surface, BACKGROUND_COLOR[0], (0, 120, SCREEN_WIGHT, 630))
    pygame.draw.rect(surface, BACKGROUND_COLOR[1], (0, 630, SCREEN_WIGHT, SCREEN_HEIGHT))


def draw_chain(surface, chain):
    chain.create_surface()
    surface.blit(chain.surface, (0, 0))


def draw_storage_pane(surface, storage):
    storage.create_surface()
    surface.blit(storage.surface, (0, 0))


def draw_restart_button(surface, button):
    button.create_surface()
    surface.blit(button.surface, (0, 0))


def draw_player1_pool(surface, player1_pool):
    player1_pool.create_surface()
    x, y = get_player_pool_position(player1_pool)
    surface.blit(player1_pool.surface, (x, y))


def draw_player2_pool(surface, player2_pool):
    player2_pool.create_surface()
    x, y = get_player_pool_position(player2_pool)
    surface.blit(player2_pool.surface, (x, y))


def draw_game_result(surface, game_result):
    surface.blit(game_result.surface, (0, 0))


def is_quit_event(events):
    for event in events:
        if event.type == pygame.QUIT:
            return True
    return False

