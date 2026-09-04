# Sudoku Project Instructions

## Project Overview

This project is a Flask-based Sudoku game being refactored from legacy Python code into a modern, modular and maintainable application.

The final application must provide:

- A working 9x9 Sudoku game
- Easy, Medium and Hard difficulty levels
- Exactly one unique solution for every generated puzzle
- Locked prefilled cells
- Immediate feedback for invalid entries
- Check Puzzle functionality
- Hint functionality
- Completion detection
- Game timer
- Top 10 leaderboard
- Local storage persistence
- Dark mode
- Responsive desktop and mobile layouts
- Accessible controls and readable UI

## Python Standards

- Use modern Python practices and clear, readable code.
- Follow PEP 8 where practical.
- Use descriptive names for variables, functions and classes.
- Keep functions small and focused on one responsibility.
- Avoid unnecessary global state.
- Prefer modular and reusable functions.
- Add type hints where they improve readability.
- Add docstrings to important functions.
- Handle errors gracefully.
- Do not introduce unnecessary dependencies.

## Application Structure

Keep responsibilities separated:

- `app.py` should primarily handle Flask routes and application flow.
- `sudoku_logic.py` should contain Sudoku generation, solving and validation logic.
- HTML templates should contain presentation structure.
- CSS should contain styling and responsive layout rules.
- JavaScript should contain client-side interaction and UI behavior.
- Tests should be separated from application code.

Do not put all functionality into a single file.

## Sudoku Rules

The Sudoku implementation must enforce:

1. The board is 9x9.
2. Every row must contain numbers 1-9 without duplicates.
3. Every column must contain numbers 1-9 without duplicates.
4. Every 3x3 box must contain numbers 1-9 without duplicates.
5. Generated puzzles must have exactly one valid solution.
6. Prefilled cells must not be editable.
7. Hints must always provide a correct value from the puzzle solution.

## Difficulty

Provide three difficulty levels:

- Easy
- Medium
- Hard

Difficulty should control the number of cells initially revealed.

Do not rely only on random removal of cells. Puzzle generation must verify that the resulting puzzle has exactly one solution.

## Frontend

The interface should:

- Work on desktop and mobile screens.
- Support both light and dark modes.
- Keep controls readable and usable.
- Use alternating visual styling for the 3x3 Sudoku boxes.
- Avoid layout shifts.
- Provide clear visual feedback for invalid entries.
- Clearly distinguish editable, prefilled, hinted and incorrect cells.

## Accessibility

Prefer accessible HTML elements and controls.

- Use meaningful labels.
- Ensure sufficient contrast.
- Make interactive controls keyboard accessible.
- Do not rely only on color to communicate important information.
- Provide useful text for status and error messages.

## Testing

Tests must be created before major refactoring.

Run the existing tests before modifying application behavior.

After every significant change:

1. Run the test suite.
2. Fix regressions before continuing.
3. Verify the application manually when appropriate.

New functionality should be tested whenever practical.

## Git Practices

Make focused changes.

Prefer small, understandable commits such as:

- `Add testing framework`
- `Refactor Sudoku logic`
- `Add difficulty levels`
- `Add timer and hints`
- `Add leaderboard`
- `Add dark mode`
- `Improve responsive styling`

Do not combine unrelated changes into one large change.

## GitHub Copilot Usage

Use GitHub Copilot as an assistant rather than blindly accepting generated code.

Before implementing significant changes:

1. Ask Copilot to explain its proposed approach.
2. Review the generated code.
3. Check that it follows these project instructions.
4. Reject or modify suggestions that are incorrect, unnecessarily complex, or inconsistent with the project.
5. Run tests after accepting changes.

When uncertain about generated code, ask Copilot to explain it before using it.

## Code Quality

Prioritize:

- Readability
- Maintainability
- Modularity
- Testability
- Clear error handling
- Consistent naming
- Minimal duplication

Do not rewrite working code unnecessarily unless there is a clear benefit.

## Important Rule

Never sacrifice Sudoku correctness for convenience.

Every generated puzzle must have exactly one solution, and all game features must use the verified solution when determining correctness.