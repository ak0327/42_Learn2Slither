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
                (0,  1): ">",
                (0, -1): "<",
                (-1,  0): "^",
                (1,  0): "v",
            }
            return self.__class__(direction_to_char.get(direction, self), self.color)

    WALL = _Element("W", Fore.WHITE)
    SNAKE_HEAD = _Element("H", Fore.CYAN)
    SNAKE_BODY = _Element("S", Fore.BLUE)
    GREEN_APPLE = _Element("G", Fore.GREEN)
    RED_APPLE = _Element("R", Fore.RED)
    EMPTY = _Element("0", Fore.LIGHTBLACK_EX)


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


class Board:
    def __init__(self, board_size=10):
        self.board_size = board_size
        self.SNAKE_INIT_BODY_LEN = 2
        self.NUM_OF_GREEN_APPLES = 2
        self.NUM_OF_RED_APPLES = 1

        self.SCORE_EAT_GREEN_APPLE = 1
        self.SCORE_EAT_RED_APPLE = -1
        self.SCORE_COLLISION = -1

        self.snake = deque()  # deque([head, .., tail])
        self.green_apples = []
        self.red_apples = []

        self.reset()

    def reset(self):
        self.board = np.full((self.board_size, self.board_size), BoardElements.EMPTY, dtype=str)

        self._init_snake()
        self._init_apples()

        self.done = False
        self.score = 0

        # self.update_board()
        # self.draw()

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

    def _put_apple(self, apple):
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

    def _is_wall_collision(self, pos):
        if pos[0] < 0 or self.board_size <= pos[0]:
            return True
        if pos[1] < 0 or self.board_size <= pos[1]:
            return True
        return False

    def _is_collision(self, pos):
        """
        Check for collisions with walls and own body
        """
        if self._is_wall_collision(pos):
            return True
        if pos in self.snake:
            return True
        return False

    def _move_to_direction(self):
        next_head_y = self.snake[0][0] + self.snake_direction[0]
        next_head_x = self.snake[0][1] + self.snake_direction[1]
        new_head = (next_head_y, next_head_x)

        if self._is_collision(new_head):
            self.done = True
            self.score = self.SCORE_COLLISION
            return Status.FAILURE

        if new_head in self.green_apples:
            self.score += self.SCORE_EAT_GREEN_APPLE
            self.green_apples.remove(new_head)
            self._extend_snake()
            self._put_apple(apple=BoardElements.GREEN_APPLE)
        elif new_head in self.red_apples:
            self.score += self.SCORE_EAT_RED_APPLE
            self.red_apples.remove(new_head)
            self._shrink_snake()
            self._put_apple(apple=BoardElements.RED_APPLE)
            if len(self.snake) == 0:
                self.done = True
                return Status.FAILURE

        self.snake.appendleft(new_head)
        self.snake.pop()
        return Status.SUCCESS

    def step(self, action):
        if self.done:
            return self.board, self.score, self.done

        if action == MoveTo.UP:
            self.snake_direction = MoveTo.UP.direction
        elif action == MoveTo.DOWN:
            self.snake_direction = MoveTo.DOWN.direction
        elif action == MoveTo.LEFT:
            self.snake_direction = MoveTo.LEFT.direction
        else:
            self.snake_direction = MoveTo.RIGHT.direction

        self._move_to_direction()
        self.update_board()
        return self.board, self.score, self.done

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
        print(f"Snake Direction: {self.snake_direction}")
        print(f"Snake          : {self.snake}")
        print(f"GreenApples    : {self.green_apples}")
        print(f"RedApples      : {self.red_apples}")
        print(f"Score          : {self.score}")
        print(f"Game Done      : {self.done}")
        print("-" * 20)
