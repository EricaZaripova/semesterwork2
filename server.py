import socket
from _thread import *
import pickle
from classes import Game, Chain, Storage, PlayerPool, ResultPane

server = "192.168.0.107"
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    str(e)

s.listen(2)
print("Waiting for a connection, Server Started")

connected = set()
games = {}
id_count = 0


def threaded_client(conn, p, game_id):
    global id_count
    conn.send(str.encode(str(p)))

    while True:
        try:
            data = conn.recv(4096).decode()

            if game_id in games:
                game = games[game_id]

                if not data:
                    break
                else:
                    if data == "restart":
                        game.chain = Chain()
                        game.storage = Storage(chain)
                        game.result_pane = ResultPane()
                        game.turn = 0
                        game.players[0].chain = chain
                        game.players[0].pool = []
                        game.players[1].chain = chain
                        game.players[1].pool = []
                        for _ in range(7):
                            player1.add_domino(storage.take_domino())
                        for _ in range(7):
                            player2.add_domino(storage.take_domino())

                    conn.sendall(pickle.dumps('1'))
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
    conn, addr = s.accept()
    print("Connected to:", addr)

    id_count += 1
    p = 0
    game_id = (id_count - 1)//2
    if id_count % 2 == 1:
        chain = Chain()
        storage = Storage(chain)
        result_pane = ResultPane()
        player1 = PlayerPool(chain, 0)
        player2 = PlayerPool(chain, 1)
        for _ in range(7):
            player1.add_domino(storage.take_domino())
        for _ in range(7):
            player2.add_domino(storage.take_domino())
        games[game_id] = Game(player1, player2, game_id, chain, storage, result_pane)
        games[game_id].p1connect = True
        print("Creating a new game...")
    else:
        games[game_id].p2connect = True
        p = 1

    start_new_thread(threaded_client, (conn, p, game_id))
