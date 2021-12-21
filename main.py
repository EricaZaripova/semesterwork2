import pygame
import sys

from classes import RestartGameButton, Network
from functions import draw_background, is_quit_event, is_available_moves, check_end_game, draw_chain, draw_storage_pane, \
    draw_game_result, draw_restart_button, draw_player_pool, draw_opponent_pool, draw_waiting_pane
from parameters import SCREEN_WIGHT, SCREEN_HEIGHT, WINDOW_TITLE


pygame.init()
screen = pygame.display.set_mode((SCREEN_WIGHT, SCREEN_HEIGHT))
pygame.display.set_caption(WINDOW_TITLE)


def main():
    surface = pygame.Surface(screen.get_size()).convert()
    clock = pygame.time.Clock()

    n = Network()
    p_num = int(n.get_p())
    print("You are player", p_num)
    run = True

    while run:
        try:
            game = n.send("get")
        except Exception as e:
            run = False
            print("Couldn't get game")
            print(e)
            break

        if not (game.both_in_game()):
            draw_background(surface)
            draw_waiting_pane(surface)

            events = pygame.event.get()
            if is_quit_event(events):
                run = False
                pygame.quit()
                exit()
        else:
            button = RestartGameButton()
            chain = game.chain
            storage = game.storage
            result_pane = game.result_pane
            player_pool = game.players[p_num]

            if game.turn == p_num:
                player_turn = True

                if not chain.chain_elements:
                    chain.add_first_domino(storage.take_domino())

                while player_turn:
                    events = pygame.event.get()
                    if is_quit_event(events):
                        run = False
                        pygame.quit()
                        exit()

                    storage_action = player_pool_action = restart_action = False
                    for event in events:
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            if event.button == pygame.BUTTON_LEFT:
                                storage_action = storage.click(event.pos)
                                player_pool_action = player_pool.click(event.pos)
                                restart_action = button.click(event.pos)

                        if player_pool_action:
                            player_turn = False
                            game.turn = (p_num-1)*(-1)

                        if restart_action:
                            game = n.send("restart")
                            break

                        if player_pool_action or (storage_action and not is_available_moves(player_pool)):
                            game_result = check_end_game(player_pool, game.players[(p_num-1)*(-1)], storage)
                            if game_result != p_num and game_result != 2:
                                game_result = (-1) * (game_result - 1)
                            if game_result:
                                result_pane.set_game_result(game_result)
                                pygame.time.delay(2000)
                                game = n.send("restart")

                screen.blit(surface, (0, 0))
                draw_background(surface)
                draw_storage_pane(surface, storage)
                draw_chain(surface, chain)
                draw_player_pool(surface, player_pool)
                draw_opponent_pool(surface, len(game.players[(p_num-1)*(-1)].pool))
                draw_restart_button(surface, button)
                draw_game_result(surface, result_pane)
                pygame.display.update()

                clock.tick(60)


if __name__ == '__main__':
    main()
