import random
import copy

import sudoku_logic


UNIQUE_PUZZLE = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9],
]


def assert_valid_solution(board):
    expected = set(range(1, sudoku_logic.SIZE + 1))
    assert len(board) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in board)

    for row in board:
        assert set(row) == expected

    for col in range(sudoku_logic.SIZE):
        assert {board[row][col] for row in range(sudoku_logic.SIZE)} == expected

    for start_row in range(0, sudoku_logic.SIZE, 3):
        for start_col in range(0, sudoku_logic.SIZE, 3):
            box = {
                board[row][col]
                for row in range(start_row, start_row + 3)
                for col in range(start_col, start_col + 3)
            }
            assert box == expected


def test_create_empty_board_returns_9_by_9_zero_board():
    board = sudoku_logic.create_empty_board()

    assert board == [[0] * sudoku_logic.SIZE for _ in range(sudoku_logic.SIZE)]


def test_deep_copy_is_independent():
    board = sudoku_logic.create_empty_board()
    copied_board = sudoku_logic.deep_copy(board)
    copied_board[0][0] = 1

    assert board[0][0] == sudoku_logic.EMPTY
    assert copied_board[0][0] == 1


def test_is_safe_accepts_candidate_with_no_conflict():
    board = sudoku_logic.create_empty_board()

    assert sudoku_logic.is_safe(board, 0, 0, 1)


def test_is_safe_rejects_row_conflict():
    board = sudoku_logic.create_empty_board()
    board[0][1] = 5

    assert not sudoku_logic.is_safe(board, 0, 0, 5)


def test_is_safe_rejects_column_conflict():
    board = sudoku_logic.create_empty_board()
    board[1][0] = 5

    assert not sudoku_logic.is_safe(board, 0, 0, 5)


def test_is_safe_rejects_box_conflict():
    board = sudoku_logic.create_empty_board()
    board[1][1] = 5

    assert not sudoku_logic.is_safe(board, 0, 0, 5)


def test_count_solutions_finds_one_solution():
    assert sudoku_logic.count_solutions(UNIQUE_PUZZLE) == 1


def test_count_solutions_restores_the_board():
    puzzle = copy.deepcopy(UNIQUE_PUZZLE)

    sudoku_logic.count_solutions(puzzle)

    assert puzzle == UNIQUE_PUZZLE


def test_count_solutions_stops_at_two_solutions():
    assert sudoku_logic.count_solutions(sudoku_logic.create_empty_board()) == 2


def test_count_solutions_returns_zero_for_invalid_puzzle():
    invalid = sudoku_logic.create_empty_board()
    invalid[0][0] = 1
    invalid[0][1] = 1

    assert sudoku_logic.count_solutions(invalid) == 0


def test_count_solutions_returns_zero_for_malformed_puzzle():
    malformed = sudoku_logic.create_empty_board()
    malformed[0][0] = '1'

    assert sudoku_logic.count_solutions(malformed) == 0


def test_fill_board_fills_an_empty_board():
    random.seed(0)
    board = sudoku_logic.create_empty_board()

    assert sudoku_logic.fill_board(board)
    assert_valid_solution(board)


def test_remove_cells_respects_requested_clue_count():
    random.seed(0)
    board = [[1] * sudoku_logic.SIZE for _ in range(sudoku_logic.SIZE)]

    sudoku_logic.remove_cells(board, clues=35)

    assert sum(cell != sudoku_logic.EMPTY for row in board for cell in row) == 35


def test_generate_puzzle_returns_valid_solution_and_matching_clues():
    random.seed(0)

    puzzle, solution = sudoku_logic.generate_puzzle()

    assert_valid_solution(solution)
    assert len(puzzle) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in puzzle)
    assert sum(cell != sudoku_logic.EMPTY for row in puzzle for cell in row) == 35
    for row in range(sudoku_logic.SIZE):
        for col in range(sudoku_logic.SIZE):
            if puzzle[row][col] != sudoku_logic.EMPTY:
                assert puzzle[row][col] == solution[row][col]
    assert sudoku_logic.count_solutions(puzzle) == 1


def test_generate_puzzle_respects_custom_clue_count():
    random.seed(1)

    puzzle, _ = sudoku_logic.generate_puzzle(clues=45)

    assert sum(cell != sudoku_logic.EMPTY for row in puzzle for cell in row) == 45


def test_generate_puzzle_supports_full_solution_clue_count():
    random.seed(2)

    puzzle, solution = sudoku_logic.generate_puzzle(clues=81)

    assert puzzle == solution
    assert sudoku_logic.count_solutions(puzzle) == 1


def test_generate_puzzle_rejects_invalid_clue_counts():
    for clues in (-1, 0, 16, 82, '35'):
        try:
            sudoku_logic.generate_puzzle(clues=clues)
        except ValueError:
            pass
        else:
            raise AssertionError(f'Expected ValueError for clues={clues!r}')


def test_difficulty_mapping_and_generation():
    assert sudoku_logic.clues_for_difficulty(sudoku_logic.Difficulty.EASY) == 40
    assert sudoku_logic.clues_for_difficulty(sudoku_logic.Difficulty.MEDIUM) == 35
    assert sudoku_logic.clues_for_difficulty(sudoku_logic.Difficulty.HARD) == 30
    assert sudoku_logic.clues_for_difficulty('easy') == 40
    assert sudoku_logic.clues_for_difficulty('medium') == 35
    assert sudoku_logic.clues_for_difficulty('hard') == 30

    for difficulty in [
        sudoku_logic.Difficulty.EASY,
        sudoku_logic.Difficulty.MEDIUM,
        sudoku_logic.Difficulty.HARD,
        'easy',
        'medium',
        'hard',
    ]:
        puzzle, solution = sudoku_logic.generate_puzzle_for_difficulty(difficulty)
        assert_valid_solution(solution)
        assert len(puzzle) == sudoku_logic.SIZE
        assert all(len(row) == sudoku_logic.SIZE for row in puzzle)
        assert sum(cell != sudoku_logic.EMPTY for row in puzzle for cell in row) == sudoku_logic.clues_for_difficulty(difficulty)
        assert sudoku_logic.count_solutions(puzzle) == 1
        for row in range(sudoku_logic.SIZE):
            for col in range(sudoku_logic.SIZE):
                if puzzle[row][col] != sudoku_logic.EMPTY:
                    assert puzzle[row][col] == solution[row][col]


def test_invalid_difficulty_raises_value_error():
    for difficulty in (None, '', 'expert', 'impossible', 'medium ', 'EASY', 'MEDIUM', 'HARD'):
        try:
            sudoku_logic.clues_for_difficulty(difficulty)
        except ValueError:
            pass
        else:
            raise AssertionError(f'Expected ValueError for difficulty={difficulty!r}')

    try:
        sudoku_logic.generate_puzzle_for_difficulty('invalid')
    except ValueError:
        pass
    else:
        raise AssertionError('Expected ValueError for invalid difficulty')


def test_generate_puzzle_for_difficulty_medium_matches_default_behavior():
    random.seed(0)
    puzzle, solution = sudoku_logic.generate_puzzle_for_difficulty('medium')

    assert sum(cell != sudoku_logic.EMPTY for row in puzzle for cell in row) == 35
    assert_valid_solution(solution)
    assert sudoku_logic.count_solutions(puzzle) == 1

    default_puzzle, default_solution = sudoku_logic.generate_puzzle(clues=35)
    assert sum(cell != sudoku_logic.EMPTY for row in default_puzzle for cell in row) == 35
    assert_valid_solution(default_solution)
    assert sudoku_logic.count_solutions(default_puzzle) == 1
