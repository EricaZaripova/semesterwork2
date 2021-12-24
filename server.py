from multiprocessing.connection import Listener
from _thread import *
from classes import Game, Chain, Storage


def new_game(game_id):
    chain = Chain()
    storage = Storage()
    first_domino = storage.take_domino()
    chain.add_first_domino(first_domino)
    player1_pool = []
    player2_pool = []
    for _ in range(7):
        domino = storage.take_domino()
        player1_pool.append([domino.side1, domino.side2])
    for _ in range(7):
        domino = storage.take_domino()
        player2_pool.append([domino.side1, domino.side2])

    if not game_id in games:
        games[game_id] = {}
        games[game_id]['game'] = Game(game_id)
    games[game_id]['game'].p1_pool = 7
    games[game_id]['game'].p2_pool = 7
    games[game_id]['storage'] = storage
    games[game_id]['chain'] = chain
    games[game_id]['first_domino'] = [first_domino.side1, first_domino.side2]
    games[game_id]['0'] = player1_pool
    games[game_id]['1'] = player2_pool


server = "192.168.0.107"
port = 5555

s = Listener((server, port))

print("Waiting for a connection, Server Started")

connected = set()
games = {}
id_count = 0


def threaded_client(conn, p, game_id):
    global id_count
    while True:
        try:
            data = conn.recv()

            if game_id in games:
                game = games[game_id]['game']

                if not data:
                    break
                else:
                    if data == "restart":
                        new_game(game_id)
                        game.turn = 0
                        game.last = [None, None, None]
                        game.p1_available_moves = True
                        game.p2_available_moves = True

                        conn.send(game)

                    if data == 'game':
                        conn.send(game)

                    elif data == 'storage':
                        storage = games[game_id]['storage']
                        domino = storage.domino_list.pop()
                        if game.turn == 0:
                            game.p1_pool += 1
                        else:
                            game.p2_pool += 1
                        conn.send([domino.side1, domino.side2])

                    elif data == 'first_domino':
                        conn.send(games[game_id]['first_domino'])

                    elif data == 'change_turn':
                        game.turn = (game.turn - 1) * (-1)
                        conn.send('1')

                    elif data == 'change_last':
                        game.last = [None, None, None]
                        conn.send('1')

                    elif data == "storage_len":
                        conn.send(len(games[game_id]['storage'].domino_list))

                    elif data == 'WIN':
                        game.result = p
                        conn.send(p)

                    elif data == 'STANDOFF':
                        game.result = 2
                        conn.send(2)

                    elif data == 'check_opponent':
                        if game.turn == 0:
                            conn.send(game.p2_available_moves)
                        else:
                            conn.send(game.p1_available_moves)

                    elif data == 'opponent_domino':
                        if p == 0:
                            # print('p2_pool ', game.p2_pool)
                            conn.send(game.p2_pool)
                        else:
                            # print('p1_pool ', game.p1_pool)
                            conn.send(game.p1_pool)

                    elif data == 'number':
                        conn.send(p)

                    elif data == '0':
                        conn.send(games[game_id]['0'])

                    elif data == '1':
                        conn.send(games[game_id]['1'])

                    else:
                        if game.turn == 0:
                            game.p1_pool -= 1
                        else:
                            game.p2_pool -= 1
                        game.last = data
                        conn.send('1')
            else:
                break
        except:
            break

    print("Lost connection")
    try:
        del games[game_id]
        print("Closing Game", game_id)
    except:
        pass
    id_count -= 1
    conn.close()


while True:
    conn = s.accept()
    print("Connected to:", conn)

    id_count += 1
    p = 0
    game_id = (id_count - 1)//2
    if id_count % 2 == 1:
        new_game(game_id)
        games[game_id]['game'].p1connect = True
        print("Creating a new game...")
    else:
        games[game_id]['game'].p2connect = True
        p = 1

    start_new_thread(threaded_client, (conn, p, game_id))
