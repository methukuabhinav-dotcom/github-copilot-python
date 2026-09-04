import copy

import app as app_module
import sudoku_logic


def test_index_returns_sudoku_page(client):
    response = client.get('/')

    assert response.status_code == 200
    assert response.mimetype == 'text/html'
    assert b'Sudoku Game' in response.data


def test_new_returns_9_by_9_puzzle_and_stores_game(client):
    response = client.get('/new')

    assert response.status_code == 200
    payload = response.get_json()
    puzzle = payload['puzzle']
    assert len(puzzle) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in puzzle)
    assert puzzle == app_module.CURRENT['puzzle']
    assert app_module.CURRENT['solution'] is not None


def test_new_uses_requested_clue_count(client):
    response = client.get('/new?clues=45')

    assert response.status_code == 200
    puzzle = response.get_json()['puzzle']
    assert sum(cell != sudoku_logic.EMPTY for row in puzzle for cell in row) == 45


def test_new_supports_difficulty_endpoints(client):
    for difficulty, clues in [('easy', 40), ('medium', 35), ('hard', 30)]:
        response = client.get(f'/new?difficulty={difficulty}')
        assert response.status_code == 200
        puzzle = response.get_json()['puzzle']
        assert sum(cell != sudoku_logic.EMPTY for row in puzzle for cell in row) == clues
        assert app_module.CURRENT['solution'] is not None

    response = client.get('/new')
    assert response.status_code == 200
    puzzle = response.get_json()['puzzle']
    assert sum(cell != sudoku_logic.EMPTY for row in puzzle for cell in row) == 35


def test_new_rejects_invalid_difficulty_and_conflicting_parameters(client):
    response = client.get('/new?difficulty=expert')
    assert response.status_code == 400
    assert 'difficulty' in response.get_json()['error'].lower()

    response = client.get('/new?difficulty=easy&clues=35')
    assert response.status_code == 400
    assert 'either' in response.get_json()['error'].lower()


def test_check_before_new_game_returns_error(client):
    response = client.post('/check', json={'board': sudoku_logic.create_empty_board()})

    assert response.status_code == 400
    assert response.get_json() == {'error': 'No game in progress'}


def test_check_returns_no_incorrect_cells_for_solution(client):
    client.get('/new')
    solution = copy.deepcopy(app_module.CURRENT['solution'])

    response = client.post('/check', json={'board': solution})

    assert response.status_code == 200
    assert response.get_json() == {'incorrect': []}


def test_check_reports_an_incorrect_cell(client):
    client.get('/new')
    board = copy.deepcopy(app_module.CURRENT['solution'])
    original_value = board[0][0]
    board[0][0] = (original_value % sudoku_logic.SIZE) + 1

    response = client.post('/check', json={'board': board})

    assert response.status_code == 200
    assert response.get_json() == {'incorrect': [[0, 0]]}


def test_check_reports_multiple_incorrect_cells(client):
    client.get('/new')
    board = copy.deepcopy(app_module.CURRENT['solution'])
    changed_cells = [(0, 0), (1, 1), (2, 2)]
    for row, col in changed_cells:
        board[row][col] = (board[row][col] % sudoku_logic.SIZE) + 1

    response = client.post('/check', json={'board': board})

    assert response.status_code == 200
    assert response.get_json()['incorrect'] == [list(cell) for cell in changed_cells]


def test_new_game_replaces_previous_game_state(client):
    client.get('/new')
    previous_solution = app_module.CURRENT['solution']

    client.get('/new')

    assert app_module.CURRENT['solution'] is not previous_solution
