import copy
import random
from enum import Enum

SIZE = 9
EMPTY = 0
MIN_CLUES = 17
MAX_CLUES = SIZE * SIZE


class Difficulty(Enum):
    EASY = 'easy'
    MEDIUM = 'medium'
    HARD = 'hard'


DIFFICULTY_TO_CLUES = {
    Difficulty.EASY: 40,
    Difficulty.MEDIUM: 35,
    Difficulty.HARD: 30,
}

def deep_copy(board):
    return copy.deepcopy(board)

def create_empty_board():
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]

def is_safe(board, row, col, num):
    # Check row and column
    for x in range(SIZE):
        if board[row][x] == num or board[x][col] == num:
            return False
    # Check 3x3 box
    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True


def _is_valid_board(board):
    if not isinstance(board, (list, tuple)) or len(board) != SIZE:
        return False
    if any(
        not isinstance(row, (list, tuple)) or len(row) != SIZE
        for row in board
    ):
        return False

    for row in board:
        values = [value for value in row if value != EMPTY]
        if any(
            not isinstance(value, int)
            or isinstance(value, bool)
            or value < 1
            or value > SIZE
            for value in values
        ):
            return False
        if len(values) != len(set(values)):
            return False

    for col in range(SIZE):
        values = [board[row][col] for row in range(SIZE)]
        values = [value for value in values if value != EMPTY]
        if len(values) != len(set(values)):
            return False

    for start_row in range(0, SIZE, 3):
        for start_col in range(0, SIZE, 3):
            values = [
                board[row][col]
                for row in range(start_row, start_row + 3)
                for col in range(start_col, start_col + 3)
                if board[row][col] != EMPTY
            ]
            if len(values) != len(set(values)):
                return False

    return True


def count_solutions(board, limit=2):
    if limit < 1:
        raise ValueError('limit must be at least 1')
    if not _is_valid_board(board):
        return 0

    def count_remaining_solutions():
        best_cell = None
        best_candidates = None

        for row in range(SIZE):
            for col in range(SIZE):
                if board[row][col] != EMPTY:
                    continue
                candidates = [
                    candidate
                    for candidate in range(1, SIZE + 1)
                    if is_safe(board, row, col, candidate)
                ]
                if not candidates:
                    return 0
                if best_candidates is None or len(candidates) < len(best_candidates):
                    best_cell = (row, col)
                    best_candidates = candidates

        if best_cell is None:
            return 1

        row, col = best_cell
        total = 0
        for candidate in best_candidates:
            board[row][col] = candidate
            total += count_remaining_solutions()
            board[row][col] = EMPTY
            if total >= limit:
                return limit
        return total

    return count_remaining_solutions()

def fill_board(board):
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                possible = list(range(1, SIZE + 1))
                random.shuffle(possible)
                for candidate in possible:
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate
                        if fill_board(board):
                            return True
                        board[row][col] = EMPTY
                return False
    return True

def remove_cells(board, clues):
    attempts = SIZE * SIZE - clues
    while attempts > 0:
        row = random.randrange(SIZE)
        col = random.randrange(SIZE)
        if board[row][col] != EMPTY:
            board[row][col] = EMPTY
            attempts -= 1


def clues_for_difficulty(difficulty):
    if isinstance(difficulty, Difficulty):
        return DIFFICULTY_TO_CLUES[difficulty]
    if isinstance(difficulty, str):
        for enum_value in Difficulty:
            if difficulty == enum_value.value:
                return DIFFICULTY_TO_CLUES[enum_value]
            if difficulty == enum_value.name.lower():
                return DIFFICULTY_TO_CLUES[enum_value]
    raise ValueError(f'Invalid difficulty: {difficulty!r}. Expected one of: easy, medium, hard')


def generate_puzzle_for_difficulty(difficulty, max_attempts=10):
    clues = clues_for_difficulty(difficulty)
    last_error = None
    for _ in range(max_attempts):
        try:
            return generate_puzzle(clues=clues)
        except RuntimeError as exc:
            last_error = exc
    if last_error is not None:
        raise RuntimeError(
            f'Unable to generate a puzzle with {clues} clues for difficulty {difficulty!r}'
        ) from last_error
    raise RuntimeError(f'Unable to generate a puzzle with {clues} clues for difficulty {difficulty!r}')


def generate_puzzle(clues=35):
    if not isinstance(clues, int) or isinstance(clues, bool):
        raise ValueError(f'clues must be an integer from {MIN_CLUES} to {MAX_CLUES}')
    if not MIN_CLUES <= clues <= MAX_CLUES:
        raise ValueError(f'clues must be an integer from {MIN_CLUES} to {MAX_CLUES}')

    board = create_empty_board()
    fill_board(board)
    solution = deep_copy(board)

    positions = [
        (row, col)
        for row in range(SIZE)
        for col in range(SIZE)
    ]
    random.shuffle(positions)
    current_clues = MAX_CLUES
    for row, col in positions:
        if current_clues == clues:
            break
        value = board[row][col]
        board[row][col] = EMPTY
        if count_solutions(board) == 1:
            current_clues -= 1
        else:
            board[row][col] = value

    if current_clues != clues:
        raise RuntimeError('Unable to generate a puzzle with the requested clue count')

    puzzle = deep_copy(board)
    return puzzle, solution
