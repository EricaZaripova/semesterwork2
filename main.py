import pygame

from classes import RestartGameButton, Network, Chain, PlayerPool, Domino, ResultPane
from functions import draw_background, is_quit_event, is_available_moves, check_end_game, draw_chain, draw_storage_pane, \
    draw_restart_button, draw_player_pool, draw_waiting_pane, storage_click, draw_game_result, draw_opponent_pool
from parameters import SCREEN_WIGHT, SCREEN_HEIGHT, WINDOW_TITLE, PLAYERS_COLORS, FPS


def new_game(n, p_num):
    chain = Chain()
    result_pane = ResultPane(p_num)
    button = RestartGameButton()
    player_pool = PlayerPool(p_num, chain)
    try:
        pool = n.send(str(p_num))
        for d in pool:
            player_pool.add_domino(Domino(d[0], d[1]))
    except Exception as e:
        print("Couldn't get pool")
        print(e)

    return chain, result_pane, button, player_pool


def redraw_screen(surface, n, game, chain, player_pool, button, result_pane):
    global run
    screen.blit(surface, (0, 0))
    draw_background(surface)
    draw_chain(surface, chain)
    draw_storage_pane(surface, n.send("storage_len"))
    draw_player_pool(surface, player_pool, chain, game.turn)
    draw_opponent_pool(surface, n.send('opponent_domino'))
    draw_restart_button(surface, button)
    pygame.display.update()

    if not (game.result is None):
        result_pane.set_game_result(game.result)
        draw_game_result(surface, result_pane)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                run = False
                break


def main():
    global run
    surface = pygame.Surface(screen.get_size()).convert()
    clock = pygame.time.Clock()
    n = Network()
    p_num = int(n.send('number'))
    print("Вы игрок", p_num)
    chain, result_pane, button, player_pool = new_game(n, p_num)

    run = True

    while run:
        try:
            game = n.send("game")
        except Exception as e:
            run = False
            print("Couldn't get game")
            print(e)
            break

        if not game.ready:
            screen.blit(surface, (0, 0))
            draw_background(surface)
            draw_waiting_pane(surface, 'Ждём ещё одного игрока...')
            pygame.display.update()
            clock.tick(60)

            events = pygame.event.get()
            if is_quit_event(events):
                run = False
                pygame.quit()
                exit()
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    pygame.quit()
                    exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == pygame.BUTTON_LEFT:
                        if button.click(event.pos):
                            run = False
                            break

            if not chain.chain_elements:
                first_domino = n.send("first_domino")
                chain.add_first_domino(Domino(first_domino[0], first_domino[1]))

            if game.last[2] and game.last[0] != p_num:
                if game.last[1] == 'r':
                    chain.add_to_right(Domino(game.last[2][0], game.last[2][1]), PLAYERS_COLORS[game.last[0]])
                    res = n.send("change_last")
                else:
                    chain.add_to_left(Domino(game.last[2][0], game.last[2][1]), PLAYERS_COLORS[game.last[0]])
                    res = n.send("change_last")

            try:
                redraw_screen(surface, n, game, chain, player_pool, button, result_pane)
            except:
                run = False
                break
            clock.tick(FPS)
            while game.turn == p_num and run:
                storage_action = player_pool_action = restart_action = False
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        run = False
                        pygame.quit()
                        exit()

                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == pygame.BUTTON_LEFT:
                            storage_action = storage_click(event.pos)
                            player_pool_action = player_pool.click(event.pos)
                            restart_action = button.click(event.pos)

                    if storage_action and n.send('storage_len') > 0:
                        domino = n.send("storage")
                        player_pool.add_domino(Domino(domino[0], domino[1]))

                    if player_pool_action:
                        game.turn = (game.turn - 1) * (-1)
                        res = n.send(player_pool_action)
                        res = n.send('change_turn')
                        break

                    if restart_action:
                        game.turn = (game.turn - 1) * (-1)
                        run = False
                        break

                if player_pool_action or (storage_action and not is_available_moves(player_pool)):
                    game_result = check_end_game(player_pool, n.send('check_opponent'), n.send("storage_len"))
                    if game_result:
                        res = n.send(game_result)
                        result_pane.set_game_result(res)

                try:
                    redraw_screen(surface, n, game, chain, player_pool, button, result_pane)
                except:
                    run = False
                    break
                clock.tick(FPS)


def menu_screen():
    run = True
    surface = pygame.Surface(screen.get_size()).convert()
    clock = pygame.time.Clock()

    while run:
        screen.blit(surface, (0, 0))
        draw_background(surface)
        draw_waiting_pane(surface, 'Нажмите в любом месте, чтобы начать игру')
        pygame.display.update()
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                run = False

    main()


if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIGHT, SCREEN_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)

    run = True

    while True:
        menu_screen()
