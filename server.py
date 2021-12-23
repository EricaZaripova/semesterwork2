import socket
from multiprocessing.connection import Listener
from _thread import *
import pickle
from classes import Game, Chain, Storage, PlayerPool, ResultPane
from functions import check_end_game

server = "192.168.0.107"
port = 5555

s = Listener((server, port))

# try:
#     s.bind((server, port))
# except socket.error as e:
#     str(e)

# s.listen(2)
print("Waiting for a connection, Server Started")

connected = set()
games = {}
id_count = 0


def threaded_client(conn, p, game_id):
    global id_count
    conn.send(str.encode(str(p)))

    while True:
        try:
            data = conn.recv()

            if game_id in games:
                game = games[game_id]['game']

                if not data:
                    break
                else:
                    if data == "restart":
                        chain = Chain()
                        storage = Storage()
                        first_domino = storage.take_domino()
                        chain.add_first_domino(first_domino)
                        result_pane = ResultPane()
                        player1_pool = []
                        player2_pool = []
                        for _ in range(7):
                            domino = storage.take_domino()
                            player1_pool.append([domino.side1, domino.side2])
                        for _ in range(7):
                            domino = storage.take_domino()
                            player2_pool.append([domino.side1, domino.side2])
                        games[game_id] = {}
                        games[game_id]['game'] = Game(game_id)
                        games[game_id]['game'].p1_pool = 7
                        games[game_id]['game'].p1_pool = 7
                        games[game_id]['storage'] = storage
                        games[game_id]['chain'] = chain
                        games[game_id]['result_pane'] = result_pane
                        games[game_id]['first_domino'] = [first_domino.side1, first_domino.side2]
                        games[game_id]['0'] = player1_pool
                        games[game_id]['1'] = player2_pool

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

                    elif data == 'result_pane':
                        conn.send(games[game_id]['result_pane'])

                    elif data == 'change_turn':
                        game.turn = (game.turn - 1) * (-1)

                    elif data == "storage_len":
                        conn.send(len(games[game_id]['storage'].domino_list))

                    elif data == 'check_opponent':
                        if game.turn == 0:
                            conn.send(game.p2_available_moves)
                        else:
                            conn.send(game.p1_available_moves)

                    elif data == 'opponent_domino':
                        if game.turn == 0:
                            conn.send(game.p2_pool)
                        else:
                            conn.send(game.p1_pool)

                    elif data == '0':
                        conn.send(games[game_id]['0'])

                    elif data == '1':
                        conn.send(games[game_id]['1'])

                    else:
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
        chain = Chain()
        storage = Storage()
        first_domino = storage.take_domino()
        chain.add_first_domino(first_domino)
        result_pane = ResultPane()
        player1_pool = []
        player2_pool = []
        for _ in range(7):
            domino = storage.take_domino()
            player1_pool.append([domino.side1, domino.side2])
        for _ in range(7):
            domino = storage.take_domino()
            player2_pool.append([domino.side1, domino.side2])
        games[game_id] = {}
        games[game_id]['game'] = Game(game_id)
        games[game_id]['game'].p1_pool = 7
        games[game_id]['game'].p1_pool = 7
        games[game_id]['storage'] = storage
        games[game_id]['chain'] = chain
        games[game_id]['result_pane'] = result_pane
        games[game_id]['first_domino'] = [first_domino.side1, first_domino.side2]
        games[game_id]['0'] = player1_pool
        games[game_id]['1'] = player2_pool
        games[game_id]['game'].p1connect = True
        print("Creating a new game...")
    else:
        games[game_id]['game'].p2connect = True
        p = 1

    start_new_thread(threaded_client, (conn, p, game_id))
