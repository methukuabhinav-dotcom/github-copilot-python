from flask import Flask, render_template, jsonify, request
import sudoku_logic

app = Flask(__name__)

# Keep a simple in-memory store for current puzzle and solution
CURRENT = {
    'puzzle': None,
    'solution': None,
    'difficulty': sudoku_logic.Difficulty.MEDIUM.value,
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new')
def new_game():
    difficulty_value = request.args.get('difficulty')
    clues_value = request.args.get('clues')
    difficulty = sudoku_logic.Difficulty.MEDIUM

    if difficulty_value is not None and clues_value is not None:
        return jsonify({'error': 'Provide either difficulty or clues, not both.'}), 400

    if clues_value is not None:
        try:
            clues = int(clues_value)
        except (TypeError, ValueError):
            return jsonify({'error': 'clues must be an integer.'}), 400
        puzzle, solution = sudoku_logic.generate_puzzle(clues=clues)
    else:
        if difficulty_value is None:
            difficulty = sudoku_logic.Difficulty.MEDIUM
        else:
            try:
                clues = sudoku_logic.clues_for_difficulty(difficulty_value)
                difficulty = sudoku_logic.Difficulty(difficulty_value)
            except ValueError:
                return jsonify({'error': f'Invalid difficulty: {difficulty_value!r}. Expected one of: easy, medium, hard'}), 400
            puzzle, solution = sudoku_logic.generate_puzzle(clues=clues)
            CURRENT['puzzle'] = puzzle
            CURRENT['solution'] = solution
            CURRENT['difficulty'] = difficulty.value
            return jsonify({'puzzle': puzzle})
        puzzle, solution = sudoku_logic.generate_puzzle_for_difficulty(difficulty)

    CURRENT['puzzle'] = puzzle
    CURRENT['solution'] = solution
    CURRENT['difficulty'] = difficulty.value
    return jsonify({'puzzle': puzzle})


def _valid_board_payload(board):
    return (
        isinstance(board, list)
        and len(board) == sudoku_logic.SIZE
        and all(
            isinstance(row, list)
            and len(row) == sudoku_logic.SIZE
            and all(isinstance(value, int) and not isinstance(value, bool) and 0 <= value <= sudoku_logic.SIZE for value in row)
            for row in board
        )
    )

@app.route('/check', methods=['POST'])
def check_solution():
    data = request.get_json(silent=True) or {}
    board = data.get('board')
    solution = CURRENT.get('solution')
    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400
    if not _valid_board_payload(board):
        return jsonify({'error': 'Board must be a 9x9 grid containing numbers 0-9.'}), 400
    incorrect = []
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            if board[i][j] != solution[i][j]:
                incorrect.append([i, j])
    return jsonify({'incorrect': incorrect})


@app.route('/hint', methods=['POST'])
def get_hint():
    data = request.get_json(silent=True) or {}
    board = data.get('board')
    solution = CURRENT.get('solution')
    puzzle = CURRENT.get('puzzle')
    if solution is None or puzzle is None:
        return jsonify({'error': 'No game in progress'}), 400
    if not _valid_board_payload(board):
        return jsonify({'error': 'Board must be a 9x9 grid containing numbers 0-9.'}), 400

    for row in range(sudoku_logic.SIZE):
        for col in range(sudoku_logic.SIZE):
            if puzzle[row][col] == sudoku_logic.EMPTY and board[row][col] != solution[row][col]:
                return jsonify({'row': row, 'col': col, 'value': solution[row][col]})

    return jsonify({'error': 'There are no empty or incorrect cells left.'}), 400

if __name__ == '__main__':
    app.run(debug=True)