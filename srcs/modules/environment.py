import numpy as np
import random
from collections import deque
from colorama import Fore, Style
from enum import Enum


class Status:
    SUCCESS = 0
    FAILURE = 1


class BoardElements:
    class _Element(str):
        def __new__(cls, char, color):
            obj = super().__new__(cls, char)
            obj.color = color
            return obj

        @property
        def colored(self):
            return f"{self.color}{self}{Style.RESET_ALL}"

        def with_direction(self, direction):
            direction_to_char = {
                MoveTo.UP.direction: "^",
                MoveTo.DOWN.direction: "v",
                MoveTo.LEFT.direction: "<",
                MoveTo.RIGHT.direction: ">",
            }
            return self.__class__(direction_to_char.get(direction, self), self.color)

    WALL = _Element("W", Fore.WHITE)
    SNAKE_HEAD = _Element("H", Fore.CYAN)
    SNAKE_BODY = _Element("S", Fore.BLUE)
    GREEN_APPLE = _Element("G", Fore.GREEN)
    RED_APPLE = _Element("R", Fore.RED)
    EMPTY = _Element("0", Fore.LIGHTBLACK_EX)

    _elements = [WALL, SNAKE_HEAD, SNAKE_BODY, GREEN_APPLE, RED_APPLE, EMPTY]

    @classmethod
    def all_elements(cls):
        return cls._ordered_elements


class MoveTo(Enum):
    UP = {"id": 0, "direction": (-1, 0)}
    DOWN = {"id": 1, "direction": (1, 0)}
    LEFT = {"id": 2, "direction": (0, -1)}
    RIGHT = {"id": 3, "direction": (0, 1)}

    @property
    def id(self):
        return self.value["id"]

    @property
    def direction(self):
        return self.value["direction"]

    @classmethod
    def directions(cls):
        return [direction.direction for direction in cls]

    @classmethod
    def from_id(cls, id: int) -> 'MoveTo':
        for move in cls:
            if move.value["id"] == id:
                return move
        raise ValueError(f"No MoveTo member with id {id}")


class Board:
    def __init__(self, board_size=10):
        self.board_size = board_size
        self.SNAKE_INIT_BODY_LEN = 2
        self.NUM_OF_GREEN_APPLES = 2
        self.NUM_OF_RED_APPLES = 1

        self.REWARD_JUST_MOVE = -1
        self.REWARD_EAT_GREEN_APPLE = 50
        self.REWARD_EAT_RED_APPLE = -20
        self.REWARD_GAME_OVER = -100

        self.snake = deque()  # deque([head, .., tail])
        self.green_apples = []
        self.red_apples = []

        self.reset()

    def reset(self):
        self.board = np.full((self.board_size, self.board_size), BoardElements.EMPTY, dtype=str)

        self._init_snake()
        self._init_apples()

        self.done = False
        # self.update_board()
        # self.draw()
        return self._encode_state()

    def _init_snake(self):
        head_y = random.randint(0, self.board_size - 1)
        head_x = random.randint(0, self.board_size - 1)
        snake_head = (head_y, head_x)
        self.snake = deque([snake_head])
        self.board[snake_head] = BoardElements.SNAKE_HEAD

        directions = MoveTo.directions()
        for _ in range(self.SNAKE_INIT_BODY_LEN):
            random.shuffle(directions)
            for direction in directions:
                y, x = direction[0], direction[1]
                tail_y, tail_x = self.snake[-1][0], self.snake[-1][1]
                new_tail_y = tail_y + y
                new_tail_x = tail_x + x
                new_tail = (new_tail_y, new_tail_x)

                if self._is_collision(new_tail):
                    continue

                self.snake.append(new_tail)
                self.board[new_tail] = BoardElements.SNAKE_BODY
                break

        direction_y = head_y - tail_y
        direction_x = head_x - tail_x
        self.snake_direction = (direction_y, direction_x)

    def _init_apples(self):
        self.green_apples = []
        for _ in range(self.NUM_OF_GREEN_APPLES):
            self._put_apple(apple=BoardElements.GREEN_APPLE)

        self.red_apples = []
        for _ in range(self.NUM_OF_RED_APPLES):
            self._put_apple(apple=BoardElements.RED_APPLE)

    def _put_apple(self, apple: str):
        if apple != BoardElements.GREEN_APPLE and apple != BoardElements.RED_APPLE:
            raise ValueError(f"Error: Apple must be {BoardElements.GREEN_APPLE}"
                             f" or {BoardElements.RED_APPLE}")

        empty_cells = np.argwhere(self.board == BoardElements.EMPTY)
        empty_cells += len(self.snake)
        if len(empty_cells) == 0:
            raise ValueError("Error: No empty cell")

        while True:
            y = random.randint(0, self.board_size - 1)
            x = random.randint(0, self.board_size - 1)
            if self.board[y, x] != BoardElements.EMPTY:
                continue

            self.board[y, x] = apple
            if apple == BoardElements.GREEN_APPLE:
                self.green_apples.append((y, x))
            else:
                self.red_apples.append((y, x))
            break

    def _extend_snake(self):
        """
        Snake's length increase by 1
        """
        tail = self.snake[-1]
        if len(self.snake) == 1:
            self.snake.append((tail[0], tail[1] + 1))
        else:
            new_tail_y = 2 * tail[0] - self.snake[-2][0]
            new_tail_x = 2 * tail[1] - self.snake[-2][1]
            self.snake.append((new_tail_y, new_tail_x))

    def _shrink_snake(self):
        if len(self.snake) == 0:
            return
        self.snake.pop()

    def _is_wall_collision(self, pos: tuple):
        if pos[0] < 0 or self.board_size <= pos[0]:
            return True
        if pos[1] < 0 or self.board_size <= pos[1]:
            return True
        return False

    def _is_collision(self, pos: tuple):
        """
        Check for collisions with walls and own body
        """
        if self._is_wall_collision(pos):
            return True
        if pos in self.snake:
            return True
        return False

    def _move_to_direction(self):
        """
        move snake
        returen reward
        """
        next_head_y = self.snake[0][0] + self.snake_direction[0]
        next_head_x = self.snake[0][1] + self.snake_direction[1]
        new_head = (next_head_y, next_head_x)

        if self._is_collision(new_head):
            self.done = True
            return self.REWARD_GAME_OVER

        reward = 0
        if new_head in self.green_apples:
            self.green_apples.remove(new_head)
            self._extend_snake()
            self._put_apple(apple=BoardElements.GREEN_APPLE)
            reward = self.REWARD_EAT_GREEN_APPLE
        elif new_head in self.red_apples:
            self.red_apples.remove(new_head)
            self._shrink_snake()
            self._put_apple(apple=BoardElements.RED_APPLE)
            reward = self.REWARD_EAT_RED_APPLE
            if len(self.snake) == 0:
                self.done = True
                return self.REWARD_GAME_OVER
        else:
            reward = self.REWARD_JUST_MOVE

        self.snake.appendleft(new_head)
        self.snake.pop()
        return reward

    def step(self, action: MoveTo):
        if self.done:
            return self.board, 0, self.done

        # action = list(MoveTo)[action]
        self.snake_direction = action.direction

        reward = self._move_to_direction()
        self.update_board()
        return self._encode_state(), reward, self.done

    def _fill_snake(self):
        for i, segment in enumerate(self.snake):
            if i == 0:
                self.board[segment] = BoardElements.SNAKE_HEAD
            else:
                self.board[segment] = BoardElements.SNAKE_BODY

    def _fill_apples(self):
        for pos in self.green_apples:
            self.board[pos] = BoardElements.GREEN_APPLE

        for pos in self.red_apples:
            self.board[pos] = BoardElements.RED_APPLE

    def update_board(self):
        self.board.fill(BoardElements.EMPTY)
        self._fill_snake()
        self._fill_apples()

    def _encode_state(self):
        """
        Encode state for agent:
        - 4 directions from head (UP, DOWN, LEFT, RIGHT)
        - Each direction has 4 features (wall, body, green apple, red apple)
        """
        NUM_DIRECTIONS = len(MoveTo)  # 4方向
        FEATURES = 4  # 各視界の特徴量(壁, 体, 緑リンゴ, 赤リンゴ）
        FEATURE_WALL = 0
        FEATURE_BODY = 1
        FEATURE_GREEN_APPLE = 2
        FEATURE_RED_APPLE = 3

        state = np.zeros((NUM_DIRECTIONS, FEATURES), dtype=np.float32)

        if len(self.snake) == 0:
            return state.flatten()[np.newaxis, :]

        head_pos = self.snake[0]
        for to in MoveTo:
            id = to.id
            direction = to.direction

            dy = direction[0]
            dx = direction[1]

            distance = 0
            distances = [0, 0, 0, 0]

            y, x = head_pos[0], head_pos[1]
            while 0 <= y < self.board_size and 0 <= x < self.board_size:
                y += dy
                x += dx
                distance += 1

                if y < 0 or self.board_size <= y or x < 0 or self.board_size <= x:
                    distances[FEATURE_WALL] = distance
                    break
                if self.board[y][x] == BoardElements.SNAKE_BODY:
                    distances[FEATURE_BODY] = distance
                    break
                if self.board[y][x] == BoardElements.GREEN_APPLE:
                    distances[FEATURE_GREEN_APPLE] = distance
                    break
                if self.board[y][x] == BoardElements.RED_APPLE:
                    distances[FEATURE_RED_APPLE] = distance
                    break

            state[id] = distances

        return state.flatten()[np.newaxis, :]  # (1, NUM_DIRECTIONS * FEATURES)

    def draw(self):
        """
        Draw current board state
        """
        print("-" * 20)
        print("Current Board State:")
        for y in range(self.board_size):
            row = ""
            for x in range(self.board_size):
                c = self.board[y, x]
                if c == BoardElements.SNAKE_HEAD:
                    # row += BoardElements.SNAKE_HEAD.colored
                    row += BoardElements.SNAKE_HEAD.with_direction(self.snake_direction).colored
                elif c == BoardElements.SNAKE_BODY:
                    row += BoardElements.SNAKE_BODY.colored
                elif c == BoardElements.GREEN_APPLE:
                    row += BoardElements.GREEN_APPLE.colored
                elif c == BoardElements.RED_APPLE:
                    row += BoardElements.RED_APPLE.colored
                else:
                    row += BoardElements.EMPTY.colored
            print(row)

        print()
        print(f" Snake Direction: {self.snake_direction}")
        print(f" Snake          : {self.snake}")
        print(f" SnakeLength    : {len(self.snake)}")
        print(f" GreenApples    : {self.green_apples}")
        print(f" RedApples      : {self.red_apples}")
        print(f" Game Done      : {self.done}")
        print("-" * 20)

    def draw_with_q_values(self, qs: np.ndarray):
        """現在の状態のQ値を可視化"""
        self.draw()  # 既存の描画
        print("\nQ-Values for each direction:")
        for direction, q_val in zip(MoveTo, qs[0]):
            print(f" {direction.name}: {q_val:.3f}")
