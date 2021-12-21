import socket
import pickle
import random
from collections import namedtuple

import pygame

from functions import get_player_pool_position, check_available_for_domino, is_available_moves, get_storage
from parameters import DOMINO_CELL_SIZE, PLAYERS_COLORS, SCREEN_HEIGHT, \
    SCREEN_WIGHT, DOMINO_INTERVAL, PLAYER1_WIN, PLAYER2_WIN, BORDER_COLOR, STORAGE_COORDS, TRANSPARENT_COLOR, \
    DOMINO_COLOR, DOMINO_DOT_COLOR, THIRD_COLOR

ChainElement = namedtuple('ChainElement', ['rect', 'domino', 'label'])


class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "192.168.0.107"
        self.port = 5555
        self.addr = (self.server, self.port)
        self.p = self.connect()

    def get_p(self):
        return self.p

    def connect(self):
        try:
            self.client.connect(self.addr)
            return self.client.recv(2048).decode()
        except:
            pass

    def send(self, data):
        try:
            self.client.send(str.encode(data))
            return pickle.loads(self.client.recv(2048))
        except socket.error as e:
            print(e)


class Game:
    def __init__(self, player1, player2, id, chain, storage, result_pane):
        self.players = (player1, player2)
        self.turn = 0
        self.id = id
        self.chain = chain
        self.storage = storage
        self.p1connect = False
        self.p2connect = False
        self.result_pane = result_pane

    def both_in_game(self):
        return self.p1connect and self.p2connect


class Domino:
    RIGHT_ORIENTATION = 1
    DOWN_ORIENTATION = 2
    LEFT_ORIENTATION = 3
    UP_ORIENTATION = 4

    VERTICAL_ORIENTATIONS = UP_ORIENTATION, DOWN_ORIENTATION
    HORIZONTAL_ORIENTATION = LEFT_ORIENTATION, RIGHT_ORIENTATION

    dots = {
        0: [],
        1: [(0, 0)],
        2: [(-2, -2), (2, 2)],
        3: [(-2, -2), (0, 0), (2, 2)],
        4: [(-2, 2), (2, 2), (2, -2), (-2, -2)],
        5: [(-2, 2), (2, 2), (0, 0), (2, -2), (-2, -2)],
        6: [(-2, 2), (0, 2), (2, 2), (2, -2), (0, -2), (-2, -2)]
    }

    def __init__(self, side1, side2):
        self.side1, self.side2 = side1, side2
        self.corner_points, self.dot_coords, self.separator_coords = self.create_coords()
        self.surface = self.create_surface()
        self.rect = self.create_rect()
        self.orientation = self.RIGHT_ORIENTATION

    def create_coords(self):
        dx, dy = DOMINO_CELL_SIZE // 6, DOMINO_CELL_SIZE // 6
        left_x0, left_y0 = - (dx * 3), 0
        right_x0, right_y0 = dx * 3, 0

        x1, y1 = - DOMINO_CELL_SIZE, DOMINO_CELL_SIZE // 2
        x2, y2 = DOMINO_CELL_SIZE, - DOMINO_CELL_SIZE // 2

        dot_coords = []
        for x0, y0, side in [(left_x0, left_y0, self.side1), (right_x0, right_y0, self.side2)]:
            for dot_x, dot_y in self.dots[side]:
                dot_coords.append((x0 + dot_x * dx, y0 + dot_y * dy))

        separator_x1, separator_y1 = 0, dy * 2
        separator_x2, separator_y2 = 0, - (dy * 2)

        return [(x1, y1), (x2, y2)], dot_coords, [(separator_x1, separator_y1), (separator_x2, separator_y2)]

    def create_surface(self):
        x1 = min(self.corner_points[0][0], self.corner_points[1][0])
        y1 = max(self.corner_points[0][1], self.corner_points[1][1])
        x2 = max(self.corner_points[0][0], self.corner_points[1][0])
        y2 = min(self.corner_points[0][1], self.corner_points[1][1])
        width, height = abs(x1 - x2), abs(y1 - y2)
        x0, y0 = width // 2, height // 2

        surface = pygame.Surface((width, height))
        surface.fill(DOMINO_COLOR)
        pygame.draw.rect(surface, BORDER_COLOR, (x0 + x1, y0 - y1, width, height), 1)
        separator_x1, separator_y1 = self.separator_coords[0]
        separator_x2, separator_y2 = self.separator_coords[1]
        pygame.draw.line(
            surface,
            BORDER_COLOR,
            (x0 + separator_x1, y0 - separator_y1),
            (x0 + separator_x2, y0 - separator_y2),
            1
        )
        for dot_x, dot_y in self.dot_coords:
            pygame.draw.circle(surface, DOMINO_DOT_COLOR, (x0 + dot_x, y0 - dot_y), DOMINO_CELL_SIZE // 6 // 2)

        return surface

    def create_rect(self):
        return pygame.Rect(
            - self.surface.get_width() // 2,
            self.surface.get_height() // 2,
            self.surface.get_width(),
            self.surface.get_height()
        )

    def rotate(self, new_orientation):
        if new_orientation == self.orientation:
            return
        if new_orientation > self.orientation:
            rotate_count = new_orientation - self.orientation
        else:
            rotate_count = new_orientation + 4 - self.orientation

        for _ in range(rotate_count):
            x1, y1 = self.corner_points[0]
            x2, y2 = self.corner_points[1]
            self.corner_points[0] = - y1, x1
            self.corner_points[1] = - y2, x2

            separator_x1, separator_y1 = self.separator_coords[0]
            separator_x2, separator_y2 = self.separator_coords[1]
            self.separator_coords[0] = - separator_y1, separator_x1
            self.separator_coords[1] = - separator_y2, separator_x2

            self.dot_coords = [(- dot_y, dot_x) for dot_x, dot_y in self.dot_coords]

        self.surface = self.create_surface()
        self.rect = self.create_rect()
        self.orientation = new_orientation

    @property
    def is_double(self):
        return self.side1 == self.side2

    @property
    def is_right_orientation(self):
        return self.orientation == self.RIGHT_ORIENTATION

    @property
    def is_left_orientation(self):
        return self.orientation == self.LEFT_ORIENTATION

    @property
    def width(self):
        return self.rect.width

    @property
    def height(self):
        return self.rect.height

    def __str__(self):
        if self.orientation == self.RIGHT_ORIENTATION:
            res = f'[{self.side1}:{self.side2}]'
        else:
            res = f'[{self.side2}:{self.side1}]'
        return res

    def __repr__(self):
        return self.__str__()


class Chain:

    def __init__(self):
        self.surface = pygame.Surface((SCREEN_WIGHT, SCREEN_HEIGHT))
        self.surface.set_colorkey(TRANSPARENT_COLOR)

        self.chain_elements = []
        self.left_line, self.right_line = None, None
        self.left_side, self.right_side = None, None
        self.left_size, self.right_size = 0, 0
        self.left_wight, self.right_wight = 630, 600

    def add_first_domino(self, domino):
        if domino.is_double:
            domino.rotate(Domino.UP_ORIENTATION)
        else:
            domino.rotate(random.choice(Domino.HORIZONTAL_ORIENTATION))

        domino_rect = domino.rect
        domino_rect[0] = 0
        self.chain_elements.append(ChainElement(domino_rect, domino, None))
        self.left_line, self.right_line = domino_rect.left, domino_rect.right

        if domino.is_double:
            self.left_side, self.right_side = domino.side1, domino.side2
        else:
            if domino.is_right_orientation:
                self.left_side, self.right_side = domino.side1, domino.side2
            if domino.is_left_orientation:
                self.left_side, self.right_side = domino.side2, domino.side1

    def add_to_right(self, domino, label):
        if not self.chain_elements:
            self.add_first_domino(domino)
            return

        if self.right_size + 2 * DOMINO_CELL_SIZE < self.right_wight:
            if domino.is_double:
                domino.rotate(Domino.UP_ORIENTATION)
            else:
                if domino.side1 == self.right_side:
                    domino.rotate(Domino.RIGHT_ORIENTATION)
                    self.right_side = domino.side2
                elif domino.side2 == self.right_side:
                    domino.rotate(Domino.LEFT_ORIENTATION)
                    self.right_side = domino.side1

            domino_rect = domino.rect
            domino_rect = pygame.Rect(
                self.right_line + 2,
                domino_rect.y,
                domino_rect.width,
                domino_rect.height
            )
            self.right_line = domino_rect.right
        else:
            if not domino.is_double:
                if domino.side1 == self.right_side:
                    domino.rotate(Domino.LEFT_ORIENTATION)
                    self.right_side = domino.side2
                elif domino.side2 == self.right_side:
                    domino.rotate(Domino.RIGHT_ORIENTATION)
                    self.right_side = domino.side1

            domino_rect = domino.rect
            domino_rect = pygame.Rect(
                self.right_line - 2 - domino_rect.width,
                domino_rect.y - 420,
                domino_rect.width,
                domino_rect.height
            )
            self.right_line = domino_rect.left
        self.chain_elements.append(ChainElement(domino_rect, domino, label))
        self.right_size += domino_rect.width

    def add_to_left(self, domino, label):
        if not self.chain_elements:
            self.add_first_domino(domino)
            return

        if self.left_size + 2 * DOMINO_CELL_SIZE < self.left_wight:
            if domino.is_double:
                domino.rotate(Domino.UP_ORIENTATION)
            else:
                if domino.side1 == self.left_side:
                    domino.rotate(Domino.LEFT_ORIENTATION)
                    self.left_side = domino.side2
                elif domino.side2 == self.left_side:
                    domino.rotate(Domino.RIGHT_ORIENTATION)
                    self.left_side = domino.side1

            domino_rect = domino.rect
            domino_rect = pygame.Rect(
                self.left_line - 2 - domino_rect.width,
                domino_rect.y,
                domino_rect.width,
                domino_rect.height
            )
            self.left_line = domino_rect.left
        else:
            if not domino.is_double:
                if domino.side1 == self.left_side:
                    domino.rotate(Domino.RIGHT_ORIENTATION)
                    self.left_side = domino.side2
                elif domino.side2 == self.left_side:
                    domino.rotate(Domino.LEFT_ORIENTATION)
                    self.left_side = domino.side1

            domino_rect = domino.rect
            domino_rect = pygame.Rect(
                self.left_line + 2,
                domino_rect.y - 420,
                domino_rect.width,
                domino_rect.height
            )
            self.left_line = domino_rect.right
        self.chain_elements.insert(0, ChainElement(domino_rect, domino, label))
        self.left_size += domino_rect.width

    def create_surface(self):
        self.surface.fill(TRANSPARENT_COLOR)
        domino_list = [
            (rect, domino, label) for rect, domino, label in self.chain_elements
        ]
        for rect, domino, label in domino_list:
            self.surface.blit(domino.surface, (rect.x + SCREEN_WIGHT // 2 - 15, SCREEN_HEIGHT // 3 - rect.y // 2))
            if label:
                pygame.draw.line(
                    self.surface,
                    PLAYERS_COLORS[label],
                    (rect.x + SCREEN_WIGHT // 2 - 10, SCREEN_HEIGHT // 3 - rect.y // 2 + rect.height + 5),
                    (rect.x + SCREEN_WIGHT // 2 + rect.width - 20, SCREEN_HEIGHT // 3 - rect.y // 2 + rect.height + 5),
                    3
                )

    @property
    def width(self):
        return self.right_line - self.left_line

    @property
    def center_line(self):
        if not self.chain_elements:
            return 0
        return (self.left_line + self.right_line) // 2

    @property
    def left_domino(self):
        _, domino, _ = self.chain_elements[0]
        return domino

    @property
    def right_domino(self):
        _, domino, _ = self.chain_elements[-1]
        return domino

    @property
    def domino_list(self):
        return [domino for _, domino, _ in self.chain_elements]


class Storage:
    def __init__(self, chain):
        self.chain = chain
        self.domino_list = [Domino(side1, side2) for side1 in range(7) for side2 in range(side1, 7)]
        random.shuffle(self.domino_list)
        self.surface = pygame.Surface((SCREEN_WIGHT, SCREEN_HEIGHT))
        self.surface.set_colorkey(TRANSPARENT_COLOR)
        self.last_chain_left, self.last_chain_right = None, None

    def create_surface(self):
        self.surface.fill(TRANSPARENT_COLOR)
        if not self.storage_size:
            return

        backside_surface = get_storage()
        self.surface.blit(backside_surface, STORAGE_COORDS)

        font = pygame.font.Font(None, 42)
        font_surface = font.render(str(self.storage_size), True, BORDER_COLOR)
        font_rect = font_surface.get_rect()

        self.surface.blit(font_surface,
                          (SCREEN_WIGHT // 2 - font_rect.width, SCREEN_HEIGHT // 2 - 0.75 * font_rect.height))

    @property
    def storage_size(self):
        return len(self.domino_list)

    @property
    def is_empty(self):
        return len(self.domino_list) == 0

    def take_domino(self):
        return self.domino_list.pop()

    def click(self, player_pool, pos):
        if not self.storage_size or not is_available_moves(player_pool):
            return False

        domino_rect = pygame.Rect(STORAGE_COORDS[0], STORAGE_COORDS[1], 4 * DOMINO_CELL_SIZE, 2 * DOMINO_CELL_SIZE)
        if domino_rect.collidepoint(pos[0], pos[1]):
            domino = self.domino_list.pop()
            player_pool.add_domino(domino)
            self.last_chain_left, self.last_chain_right = self.chain.left_side, self.chain.right_side
            return True

        return False

    def get_last_chain_sides(self):
        return self.last_chain_left, self.last_chain_right


class RestartGameButton:
    def __init__(self):
        self.surface = pygame.Surface((SCREEN_WIGHT, SCREEN_HEIGHT))
        self.surface.set_colorkey(TRANSPARENT_COLOR)
        self.font = pygame.font.Font(None, 24)
        self.rect = pygame.Rect(DOMINO_CELL_SIZE, SCREEN_HEIGHT - 75, 5 * DOMINO_CELL_SIZE, DOMINO_CELL_SIZE)

    def create_surface(self):
        self.surface.fill(TRANSPARENT_COLOR)

        button_surface = pygame.Surface((5 * DOMINO_CELL_SIZE, DOMINO_CELL_SIZE))
        button_surface.fill(THIRD_COLOR)
        pygame.draw.rect(button_surface, BORDER_COLOR, (0, 0, 5 * DOMINO_CELL_SIZE, DOMINO_CELL_SIZE), 1)
        self.surface.blit(button_surface, (DOMINO_CELL_SIZE, SCREEN_HEIGHT - 75))

        font_surface = self.font.render('Начать заново', True, BORDER_COLOR)

        self.surface.blit(font_surface,
                          (DOMINO_CELL_SIZE + 15, SCREEN_HEIGHT - 68))

    def click(self, pos):
        if self.rect.collidepoint(pos[0], pos[1]):
            return True
        return False


class PlayerPool:
    PANE_WIDTH = SCREEN_WIGHT
    PANE_HEIGHT = SCREEN_HEIGHT - DOMINO_CELL_SIZE

    TO_LEFT_BUTTON_COORDS = ((1, 2), (3, 1), (3, 3))
    TO_RIGHT_BUTTON_COORDS = ((1, 1), (3, 2), (1, 3))
    ARROW_COLOR = (255, 255, 255)

    def __init__(self, chain, number):
        self.pool = []
        self.chain = chain
        self.number = number
        self.color = PLAYERS_COLORS[number]
        self.surface = pygame.Surface((self.PANE_WIDTH, self.PANE_HEIGHT))
        self.surface.set_colorkey(TRANSPARENT_COLOR)

    def create_surface(self):
        self.surface.fill(TRANSPARENT_COLOR)

        if not self.pool:
            return

        domino_block_width = DOMINO_INTERVAL * self.pool_size
        block_x0, block_y0 = self.PANE_WIDTH // 2 - domino_block_width // 2, DOMINO_CELL_SIZE
        for number, pool_element in enumerate(self.pool, 0):
            domino = pool_element['domino']
            domino_rect = pygame.Rect(block_x0 + number * DOMINO_INTERVAL, block_y0, DOMINO_CELL_SIZE, 2 * DOMINO_CELL_SIZE)
            pool_element['rect'] = domino_rect
            self.surface.blit(domino.surface, domino_rect)

            available_for_left, available_for_right = check_available_for_domino(domino, self.chain)

            delta_x = delta_y = DOMINO_CELL_SIZE // 8
            if available_for_left:
                x0, y0 = domino_rect.x, domino.rect.y - DOMINO_CELL_SIZE // 2
                arrow_coords = [(x0 + delta_x * x, y0 + delta_y * y) for x, y in self.TO_LEFT_BUTTON_COORDS]
                pygame.draw.polygon(self.surface, self.ARROW_COLOR, arrow_coords)
                pool_element['append_to_left_rect'] = pygame.Rect(x0, y0, DOMINO_CELL_SIZE // 2, DOMINO_CELL_SIZE // 2)
            else:
                pool_element['append_to_left_rect'] = None

            if available_for_right:
                x0, y0 = domino_rect.x + DOMINO_CELL_SIZE // 2, domino.rect.y - DOMINO_CELL_SIZE // 2
                arrow_coords = [(x0 + delta_x * x, y0 + delta_y * y) for x, y in self.TO_RIGHT_BUTTON_COORDS]
                pygame.draw.polygon(self.surface, self.ARROW_COLOR, arrow_coords)
                pool_element['append_to_right_rect'] = pygame.Rect(x0, y0, DOMINO_CELL_SIZE // 2, DOMINO_CELL_SIZE // 2)
            else:
                pool_element['append_to_right_rect'] = None

    @property
    def pool_size(self):
        return len(self.pool)

    @property
    def is_empty(self):
        return len(self.pool) == 0

    @property
    def domino_list(self):
        return [pool_element['domino'] for pool_element in self.pool]

    def add_domino(self, domino):
        domino.rotate(Domino.UP_ORIENTATION)
        self.pool.append(
            {
                'rect': None,
                'append_to_left_rect': None,
                'append_to_right_rect': None,
                'domino': domino
            }
        )

    def click(self, pos):
        pane_x, pane_y = get_player_pool_position(self)
        click_x, click_y = pos[0] - pane_x, pos[1] - pane_y

        pane_rect = self.surface.get_rect()
        if not pane_rect.collidepoint(click_x, click_y):
            return False

        for pool_element in self.pool:
            left_arrow_rect = pool_element['append_to_left_rect']
            right_arrow_rect = pool_element['append_to_right_rect']
            domino = pool_element['domino']

            if left_arrow_rect and left_arrow_rect.collidepoint(click_x, click_y):
                self.chain.add_to_left(domino, self.color)
                break

            if right_arrow_rect and right_arrow_rect.collidepoint(click_x, click_y):
                self.chain.add_to_right(domino, self.color)
                break
        else:
            return False

        self.pool.remove(pool_element)
        return True


class ResultPane:
    def __init__(self):
        self.surface = pygame.Surface((SCREEN_WIGHT, SCREEN_HEIGHT))
        self.surface.set_colorkey(TRANSPARENT_COLOR)
        self.game_result = None
        self.create_surface()

    def set_game_result(self, game_result):
        self.game_result = game_result
        self.create_surface()

    def create_surface(self):
        self.surface.fill(TRANSPARENT_COLOR)
        if not self.game_result:
            return

        if self.game_result == PLAYER1_WIN:
            msg = 'Вы победили!'
        elif self.game_result == PLAYER2_WIN:
            msg = 'Вы проиграли...'
        else:
            msg = 'Ничья'

        x1, y1 = SCREEN_WIGHT // 2 - DOMINO_CELL_SIZE * 6, SCREEN_HEIGHT // 2 - DOMINO_CELL_SIZE * 2
        pygame.draw.rect(self.surface, THIRD_COLOR, (x1, y1, DOMINO_CELL_SIZE * 12, DOMINO_CELL_SIZE * 4))

        font_result = pygame.font.Font(None, 36)
        result_surface = font_result.render(msg, True, BORDER_COLOR)

        result_rect = result_surface.get_rect()
        self.surface.blit(
            result_surface,
            (SCREEN_WIGHT // 2 - result_rect.width // 2, SCREEN_HEIGHT // 2 - result_rect.height // 2)
        )
