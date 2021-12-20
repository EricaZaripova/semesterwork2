import pygame
import sys

from classes import Chain, PlayerPool, Storage, ResultPane, RestartGameButton, Network
from functions import draw_background, is_quit_event, is_available_moves, check_end_game, draw_chain, draw_storage_pane, \
    draw_player1_pool, draw_game_result, draw_player2_pool, draw_restart_button
from parameters import SCREEN_WIGHT, SCREEN_HEIGHT, WINDOW_TITLE, PLAYER1_MOVE, END_GAME


pygame.init()
screen = pygame.display.set_mode((SCREEN_WIGHT, SCREEN_HEIGHT))
pygame.display.set_caption(WINDOW_TITLE)


def main():
    surface = pygame.Surface(screen.get_size()).convert()
    clock = pygame.time.Clock()

    n = Network()
    player = int(n.get_p())
    print("You are player", player)
    run = True

    while True:
        try:
            game = n.send("get")
        except:
            run = False
            print("Couldn't get game")
            break

        chain = Chain()

        player1_pool = PlayerPool(chain, 0)
        player2_pool = PlayerPool(chain, 1)
        storage = Storage(chain)
        button = RestartGameButton()

        chain.add_first_domino(storage.take_domino())

        result_pane = ResultPane()
        next_mode = game_mode = PLAYER1_MOVE
        resume_game = True

        while resume_game:
            events = pygame.event.get()
            if is_quit_event(events):
                pygame.quit()
                exit()

            if game_mode == PLAYER1_MOVE:
                storage_action = player_pool_action = restart_action = False
                for event in events:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == pygame.BUTTON_LEFT:
                            storage_action = storage.click(event.pos)
                            player_pool_action = player1_pool.click(event.pos)
                            restart_action = button.click(event.pos)

                    if restart_action:
                        resume_game = False
                        break

                    if player_pool_action or (storage_action and not is_available_moves(player1_pool)):
                        game_result = check_end_game(player1_pool, player2_pool, storage)
                        if game_result:
                            result_pane.set_game_result(game_result)
                            next_mode = END_GAME

            if game_mode == END_GAME:
                for event in events:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            pygame.quit()
                            exit()
                        if event.key == pygame.K_KP_ENTER or event.key == 13:
                            resume_game = False
                            break

            screen.blit(surface, (0, 0))
            draw_background(surface)
            draw_storage_pane(surface, storage)
            draw_chain(surface, chain)
            draw_player1_pool(surface, player1_pool)
            draw_player2_pool(surface, player2_pool)
            draw_restart_button(surface, button)
            draw_game_result(surface, result_pane)
            pygame.display.update()

            clock.tick(60)

            game_mode = next_mode


if __name__ == '__main__':
    main()
