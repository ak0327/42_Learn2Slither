from srcs.modules.environment import Board, BoardElements, Status, MoveTo

import pytest
from collections import deque


@pytest.fixture
def setup_board():
    """
      0123456789 x
    0 __________
    1 __________
    2 __________
    3 __________
    4 _____R____
    5 ___SS>____
    6 ____GG____
    7 __________
    8 __________
    9 __________
    y
    """
    board = Board(board_size=10)
    board.snake = deque([(5, 5), (5, 4), (5, 3)])
    board.snake_direction = MoveTo.RIGHT.direction
    board.done = False

    board.green_apples = [(6, 4), (6, 5)]
    board.red_apples = [(4, 5)]
    board.update_board()
    # board.draw()
    return board


class TestEnvironmentSnakeMovement:
    @staticmethod
    def _assert_state(
            board: Board,
            expected_snake: [deque] = None,
            expected_snake_direction: [tuple] = None,
            expected_green_apples: [list] = None,
            expected_in_green_apples: [tuple] = None,
            expected_num_of_green_apples: [int] = None,
            expected_red_apples: [list] = None,
            expected_in_red_apples: [tuple] = None,
            expected_num_of_red_apples: [int] = None,
            expected_done: [bool] = None,
            expected_reward: [int] = None,
            actual_reward: [int] = None,
    ):
        if expected_snake is not None:
            assert board.snake == expected_snake
        if expected_snake_direction is not None:
            assert board.snake_direction == expected_snake_direction

        if expected_green_apples is not None:
            assert board.green_apples == expected_green_apples
        if expected_in_green_apples is not None:
            assert expected_in_green_apples in board.green_apples
        if expected_num_of_green_apples is not None:
            assert len(board.green_apples) == expected_num_of_green_apples

        if expected_red_apples is not None:
            assert board.red_apples == expected_red_apples
        if expected_in_red_apples is not None:
            assert expected_in_red_apples in board.red_apples
        if expected_num_of_red_apples is not None:
            assert len(board.red_apples) == expected_num_of_red_apples

        if expected_done is not None:
            assert board.done == expected_done

        if expected_reward is not None and actual_reward is not None:
            assert actual_reward == expected_reward

    def test_move_without_eating(self, setup_board):
        """
        snake moves without eat

          0123456789 x  0123456789 x
        0 __________    __________
        1 __________    __________
        2 __________    __________
        3 __________    __________
        4 _____R____    _____R____
        5 ___SS>____    ____SS>___
        6 ____GG____    ____GG____
        7 __________    __________
        8 __________    __________
        9 __________    __________
        y               anyware G pops
        """
        board = setup_board
        _, actual_reward, _ = board.step(action=MoveTo.RIGHT)

        # before move [(5, 5), (5, 4), (5, 3)]
        # after move  [(5, 6), (5, 5), (5, 4)]

        expected_snake = deque([(5, 6), (5, 5), (5, 4)])
        expected_snake_direction = MoveTo.RIGHT.direction
        expected_green_apples = [(6, 4), (6, 5)]
        expected_red_apples = [(4, 5)]
        expected_reward = board.REWARD_JUST_MOVE
        expected_done = False

        self._assert_state(
            board=board,
            expected_snake=expected_snake,
            expected_snake_direction=expected_snake_direction,
            expected_green_apples=expected_green_apples,
            expected_red_apples=expected_red_apples,
            expected_reward=expected_reward,
            actual_reward=actual_reward,
            expected_done=expected_done,
        )

    def test_move_with_green_apple(self, setup_board):
        """
        The snake eats a green apple:
          Snake's length increase by 1
          A new green apple appears on the board

          0123456789 x  0123456789 x
        0 __________    __________
        1 __________    __________
        2 __________    __________
        3 __________    __________
        4 _____R____    _____R____
        5 ___SSv____    ___SSS____
        6 ____GG____    ____Gv____
        7 __________    __________
        8 __________    __________
        9 __________    __________
        y               anyware G pops
        """
        board = setup_board
        _, actual_reward, _ = board.step(action=MoveTo.DOWN)
        # board.draw()

        expected_snake = deque([(6, 5), (5, 5), (5, 4), (5, 3)])
        expected_snake_direction = MoveTo.DOWN.direction
        expected_in_green_apples = (6, 4)
        expected_num_of_green_apples = 2
        expected_red_apples = [(4, 5)]
        expected_reward = board.REWARD_EAT_GREEN_APPLE
        expected_done = False

        self._assert_state(
            board=board,
            expected_snake=expected_snake,
            expected_snake_direction=expected_snake_direction,
            expected_in_green_apples=expected_in_green_apples,
            expected_num_of_green_apples=expected_num_of_green_apples,
            expected_red_apples=expected_red_apples,
            expected_reward=expected_reward,
            actual_reward=actual_reward,
            expected_done=expected_done,
        )

    def test_move_with_red_apple(self, setup_board):
        """
        The snake eats a red apple:
          Snake’s length decrease by 1.
          A new red apple appears on the board.

          0123456789 x  0123456789 x
        0 __________    __________
        1 __________    __________
        2 __________    __________
        3 __________    __________
        4 _____R____    _____^____
        5 ___SS^____    _____S____
        6 ____GG____    ____GG____
        7 __________    __________
        8 __________    __________
        9 __________    __________
        y               anyware R pops
        """
        board = setup_board
        _, actual_reward, _ = board.step(action=MoveTo.UP)
        # board.draw()

        expected_snake = deque([(4, 5), (5, 5)])
        expected_snake_direction = MoveTo.UP.direction
        expected_green_apples = [(6, 4), (6, 5)]
        expected_num_of_red_apples = 1
        expected_reward = board.REWARD_EAT_RED_APPLE
        expected_done = False

        self._assert_state(
            board=board,
            expected_snake=expected_snake,
            expected_snake_direction=expected_snake_direction,
            expected_green_apples=expected_green_apples,
            expected_num_of_red_apples=expected_num_of_red_apples,
            expected_reward=expected_reward,
            actual_reward=actual_reward,
            expected_done=expected_done,
        )

    def test_snake_length_drops_to_zero(self, setup_board):
        """
        If the snake’s length drops to 0:
          Game over
          this training session ends.

          0123456789    0123456789  0123456789  0123456789
        0 __________    __________  __________  __________
        1 __________    __________  __________  __________
        2 __________    __________  __________  __________
        3 __________    __________  __________  __________
        4 __________    __________  __________  __________
        5 ___SS>R___    _____S>R__  _______>R_  __________
        6 ____GG____    ____GG____  ____GG____  ____GG____
        7 __________    __________  __________  __________
        8 __________    __________  __________  __________
        9 __________    __________  __________  __________
        y
        """
        board = setup_board
        # board.draw()

        board.red_apples = [(5, 6)]
        board.update_board()
        _, actual_reward, _ = board.step(action=MoveTo.RIGHT)
        # board.draw()

        expected_snake = deque([(5, 6), (5, 5)])
        expected_num_of_green_apples = 2
        expected_num_of_red_apples = 1
        expected_reward = board.REWARD_EAT_RED_APPLE
        expected_done = False

        self._assert_state(
            board=board,
            expected_snake=expected_snake,
            expected_num_of_green_apples=expected_num_of_green_apples,
            expected_num_of_red_apples=expected_num_of_red_apples,
            expected_reward=expected_reward,
            actual_reward=actual_reward,
            expected_done=expected_done,
        )

        board.red_apples = [(5, 7)]
        _, actual_reward, _ = board.step(action=MoveTo.RIGHT)
        # board.draw()

        expected_snake = deque([(5, 7)])
        expected_num_of_green_apples = 2
        expected_num_of_red_apples = 1
        expected_reward = board.REWARD_EAT_RED_APPLE
        expected_done = False

        self._assert_state(
            board=board,
            expected_snake=expected_snake,
            expected_num_of_green_apples=expected_num_of_green_apples,
            expected_num_of_red_apples=expected_num_of_red_apples,
            expected_reward=expected_reward,
            actual_reward=actual_reward,
            expected_done=expected_done,
        )

        board.red_apples = [(5, 8)]
        _, actual_reward, _ = board.step(action=MoveTo.RIGHT)
        # board.draw()

        expected_snake = deque([])
        expected_num_of_green_apples = 2
        expected_num_of_red_apples = 1
        expected_reward = board.REWARD_GAME_OVER
        expected_done = True

        self._assert_state(
            board=board,
            expected_snake=expected_snake,
            expected_num_of_green_apples=expected_num_of_green_apples,
            expected_num_of_red_apples=expected_num_of_red_apples,
            expected_reward=expected_reward,
            actual_reward=actual_reward,
            expected_done=expected_done,
        )


    def test_collision_with_wall(self, setup_board):
        """
        If the snake hits a wall:
          Game over
          this training session ends

          0123456789 x  0123456789 x
        0 __________    __________
        1 __________    __________
        2 __________    __________
        3 __________    __________
        4 _____R____    _____R____
        5 ___SS>____    ________SS>
        6 ____GG____    ____GG____
        7 __________    __________
        8 __________    __________
        9 __________    __________
        y
        """
        board = setup_board
        for _ in range(4):
            _, actual_reward, _ = board.step(action=MoveTo.RIGHT)
            # board.draw()
            expected_reward = board.REWARD_JUST_MOVE
            expected_done = False

            self._assert_state(
                board=board,
                expected_reward=expected_reward,
                actual_reward=actual_reward,
                expected_done=expected_done,
            )

        _, actual_reward, _ = board.step(action=MoveTo.RIGHT)
        # board.draw()

        expected_reward = board.REWARD_GAME_OVER
        expected_done = True

        self._assert_state(
            board=board,
            expected_reward=expected_reward,
            actual_reward=actual_reward,
            expected_done=expected_done,
        )

    def test_collision_with_self(self, setup_board):
        """
        If the snake collides with its own tail:
          Game over
          this training session ends.

          0123456789 x
        0 __________
        1 __________
        2 __________
        3 __________
        4 _____R____
        5 ___SS<____
        6 ____GG____
        7 __________
        8 __________
        9 __________
        y
        """
        board = setup_board
        board.snake_direction = MoveTo.LEFT.direction
        # board.draw()
        _, actual_reward, _ = board.step(action=MoveTo.LEFT)

        expected_reward = board.REWARD_GAME_OVER
        expected_done = True

        self._assert_state(
            board=board,
            expected_reward=expected_reward,
            actual_reward=actual_reward,
            expected_done=expected_done,
        )
