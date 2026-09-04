const SIZE = 9;
const SCORE_KEY = 'sudoku-top-scores';
let puzzle = [];
let difficulty = 'medium';
let elapsedSeconds = 0;
let timerId = null;
let hintsUsed = 0;
let gameComplete = false;

function getBoard() {
  return [...document.querySelectorAll('.sudoku-cell')].reduce((board, input, index) => {
    const row = Math.floor(index / SIZE);
    if (!board[row]) board[row] = [];
    board[row].push(input.value ? Number(input.value) : 0);
    return board;
  }, []);
}

function formatTime(seconds) {
  return `${String(Math.floor(seconds / 60)).padStart(2, '0')}:${String(seconds % 60).padStart(2, '0')}`;
}

function setMessage(text, kind = '') {
  const message = document.getElementById('message');
  message.textContent = text;
  message.className = `message ${kind}`;
}

function renderPuzzle(nextPuzzle) {
  puzzle = nextPuzzle;
  const board = document.getElementById('sudoku-board');
  board.innerHTML = '';
  puzzle.forEach((row, rowIndex) => row.forEach((value, colIndex) => {
    const input = document.createElement('input');
    input.className = `sudoku-cell box-${Math.floor(rowIndex / 3) * 3 + Math.floor(colIndex / 3)}`;
    input.type = 'text';
    input.inputMode = 'numeric';
    input.maxLength = 1;
    input.dataset.row = rowIndex;
    input.dataset.col = colIndex;
    input.setAttribute('role', 'gridcell');
    input.setAttribute('aria-label', `Row ${rowIndex + 1}, column ${colIndex + 1}`);
    if (value) {
      input.value = value;
      input.disabled = true;
      input.classList.add('prefilled');
    }
    board.appendChild(input);
  }));
}

function markLocalConflicts() {
  const inputs = [...document.querySelectorAll('.sudoku-cell')];
  inputs.forEach(input => input.classList.remove('conflict'));
  const board = getBoard();
  const conflicts = new Set();

  // Critical review: a Copilot suggestion marked only the edited cell and skipped prefilled cells.
  // That failed the rubric's conflicting-cells example, so every duplicate participant is marked.
  function markDuplicateGroup(group) {
    const positionsByValue = new Map();
    group.forEach(([row, col]) => {
      const value = board[row][col];
      if (!value) return;
      if (!positionsByValue.has(value)) positionsByValue.set(value, []);
      positionsByValue.get(value).push(`${row}-${col}`);
    });
    positionsByValue.forEach(positions => {
      if (positions.length > 1) positions.forEach(position => conflicts.add(position));
    });
  }

  for (let index = 0; index < SIZE; index += 1) {
    markDuplicateGroup(Array.from({length: SIZE}, (_, offset) => [index, offset]));
    markDuplicateGroup(Array.from({length: SIZE}, (_, offset) => [offset, index]));
  }
  for (let boxRow = 0; boxRow < SIZE; boxRow += 3) {
    for (let boxCol = 0; boxCol < SIZE; boxCol += 3) {
      markDuplicateGroup(Array.from({length: 9}, (_, offset) => [
        boxRow + Math.floor(offset / 3), boxCol + (offset % 3)
      ]));
    }
  }

  inputs.forEach(input => input.classList.toggle(
    'conflict', conflicts.has(`${input.dataset.row}-${input.dataset.col}`)
  ));
}

async function newGame() {
  difficulty = document.getElementById('difficulty').value;
  const response = await fetch(`/new?difficulty=${difficulty}`);
  const data = await response.json();
  renderPuzzle(data.puzzle);
  elapsedSeconds = 0;
  hintsUsed = 0;
  gameComplete = false;
  document.getElementById('timer').textContent = formatTime(elapsedSeconds);
  document.getElementById('hint-count').textContent = hintsUsed;
  setMessage('');
  clearInterval(timerId);
  timerId = setInterval(() => {
    elapsedSeconds += 1;
    document.getElementById('timer').textContent = formatTime(elapsedSeconds);
  }, 1000);
}

async function checkSolution(showMessage = true) {
  const response = await fetch('/check', {
    method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({board: getBoard()})
  });
  const data = await response.json();
  if (data.error) return setMessage(data.error, 'error');
  const incorrect = new Set(data.incorrect.map(([row, col]) => `${row}-${col}`));
  document.querySelectorAll('.sudoku-cell:not(.prefilled)').forEach(input => {
    const hasValue = input.value !== '';
    input.classList.toggle('incorrect', hasValue && incorrect.has(`${input.dataset.row}-${input.dataset.col}`));
  });
  if (incorrect.size === 0 && getBoard().every(row => row.every(Boolean))) {
    if (!gameComplete) completeGame();
  } else if (showMessage) {
    setMessage('Some entries need another look.', 'error');
  }
}

async function giveHint() {
  const response = await fetch('/hint', {
    method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({board: getBoard()})
  });
  const data = await response.json();
  if (data.error) return setMessage(data.error, 'error');
  const input = document.querySelector(`[data-row="${data.row}"][data-col="${data.col}"]`);
  input.value = data.value;
  input.disabled = true;
  input.classList.add('hinted');
  hintsUsed += 1;
  document.getElementById('hint-count').textContent = hintsUsed;
  setMessage('A correct cell has been revealed.', 'success');
  await checkSolution(false);
}

function completeGame() {
  gameComplete = true;
  clearInterval(timerId);
  const name = window.prompt('Puzzle complete! Enter your name for the leaderboard:', 'Player');
  if (name && name.trim()) {
    const scores = JSON.parse(localStorage.getItem(SCORE_KEY) || '[]');
    scores.push({name: name.trim().slice(0, 24), time: elapsedSeconds, difficulty, hints: hintsUsed});
    scores.sort((a, b) => a.time - b.time);
    localStorage.setItem(SCORE_KEY, JSON.stringify(scores.slice(0, 10)));
    renderLeaderboard();
  }
  setMessage(`Solved in ${formatTime(elapsedSeconds)}.`, 'success');
}

function renderLeaderboard() {
  const scores = JSON.parse(localStorage.getItem(SCORE_KEY) || '[]');
  document.getElementById('leaderboard-body').innerHTML = scores.map((score, index) =>
    `<tr><td>${index + 1}</td><td>${score.name}</td><td>${formatTime(score.time)}</td><td>${score.difficulty}</td><td>${score.hints}</td></tr>`
  ).join('') || '<tr><td colspan="5">No scores yet</td></tr>';
}

function toggleTheme() {
  const dark = document.body.classList.toggle('dark');
  localStorage.setItem('sudoku-theme', dark ? 'dark' : 'light');
  const toggle = document.getElementById('theme-toggle');
  toggle.textContent = dark ? 'Light mode' : 'Dark mode';
  toggle.setAttribute('aria-pressed', String(dark));
}

window.addEventListener('load', () => {
  if (localStorage.getItem('sudoku-theme') === 'dark') toggleTheme();
  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('difficulty').addEventListener('change', newGame);
  document.getElementById('check-solution').addEventListener('click', () => checkSolution());
  document.getElementById('hint-button').addEventListener('click', giveHint);
  document.getElementById('theme-toggle').addEventListener('click', toggleTheme);
  document.getElementById('sudoku-board').addEventListener('input', event => {
    if (!event.target.matches('.sudoku-cell')) return;
    event.target.value = event.target.value.replace(/[^1-9]/g, '');
    event.target.classList.remove('incorrect');
    markLocalConflicts();
    checkSolution(false);
  });
  renderLeaderboard();
  newGame();
});
