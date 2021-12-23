import pygame

from classes import RestartGameButton, Network, Chain, PlayerPool, Domino, ResultPane
from functions import draw_background, is_quit_event, is_available_moves, check_end_game, draw_chain, draw_storage_pane, \
    draw_game_result, draw_restart_button, draw_player_pool, draw_opponent_pool, draw_waiting_pane, storage_click
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
    chain = Chain()
    result_pane = ResultPane()
    button = RestartGameButton()
    player_pool = PlayerPool(p_num, chain)
    try:
        pool = n.send(str(p_num))
        for d in pool:
            player_pool.add_domino(Domino(d[0], d[1]))
    except Exception as e:
        print("Couldn't get pool")
        print(e)

    run = True

    while run:
        try:
            game = n.send("game")
        except Exception as e:
            run = False
            print("Couldn't get game")
            print(e)
            break

        if not (game.both_in_game()):
            screen.blit(surface, (0, 0))
            draw_background(surface)
            draw_waiting_pane(surface)
            pygame.display.update()
            clock.tick(60)

            events = pygame.event.get()
            if is_quit_event(events):
                run = False
                pygame.quit()
                exit()
        else:
            events = pygame.event.get()
            if is_quit_event(events):
                run = False
                pygame.quit()
                exit()

            if not chain.chain_elements:
                first_domino = n.send("first_domino")
                chain.add_first_domino(Domino(first_domino[0], first_domino[1]))

            if game.last[2] and game.last[0] != p_num:
                if game.last[1] == 'r':
                    chain.add_to_right(Domino(game.last[2][0], game.last[2][1]), player_pool.color)
                else:
                    chain.add_to_left(Domino(game.last[2][0], game.last[2][1]), player_pool.color)

            screen.blit(surface, (0, 0))
            draw_background(surface)
            draw_chain(surface, chain)
            draw_storage_pane(surface, n.send("storage_len"))
            draw_player_pool(surface, player_pool, chain, game.turn)
            draw_opponent_pool(surface, n.send('opponent_domino'))
            draw_restart_button(surface, button)
            pygame.display.update()

            clock.tick(60)
            while game.turn == p_num:
                events = pygame.event.get()
                if is_quit_event(events):
                    run = False
                    pygame.quit()
                    exit()

                storage_action = player_pool_action = restart_action = False
                for event in events:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == pygame.BUTTON_LEFT:
                            storage_action = storage_click(event.pos)
                            player_pool_action = player_pool.click(event.pos)
                            restart_action = button.click(event.pos)

                    if storage_action:
                        domino = n.send("storage")
                        player_pool.add_domino(Domino(domino[0], domino[1]))

                    if player_pool_action:
                        game.turn = (game.turn - 1) * (-1)
                        n.send(player_pool_action)

                    if restart_action:
                        game = n.send("restart")
                        break

                if player_pool_action or (storage_action and not is_available_moves(player_pool)):
                    game_result = check_end_game(player_pool, n.send('check_opponent'), n.send("storage_len"))
                    if game_result:
                        result_pane.set_game_result(game_result)
                        pygame.time.delay(2000)
                        game = n.send("restart")

                screen.blit(surface, (0, 0))
                draw_background(surface)
                draw_chain(surface, chain)
                draw_storage_pane(surface, n.send("storage_len"))
                draw_player_pool(surface, player_pool, chain, game.turn)
                draw_opponent_pool(surface, n.send('opponent_domino'))
                draw_restart_button(surface, button)
                pygame.display.update()

                clock.tick(60)


if __name__ == '__main__':
    main()
