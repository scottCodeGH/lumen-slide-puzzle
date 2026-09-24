# CLAUDE.md

Sliding tile puzzle (4x4 by default) in Python + Pygame. Single-file app, no build step.

## Commands

```bash
pip install -r requirements-dev.txt   # pygame + pytest
python sliding_puzzle.py              # run the game (needs a display)
python -m pytest                      # headless tests in tests/
```

Headless (CI / cloud container): set `SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy` before importing the module (`tests/conftest.py` does this). Note `pygame.init()` and font creation run at import time.

## Layout

- `sliding_puzzle.py` — everything: constants (window/tile sizes, colors, fonts) at top, then
  - `Tile` — `grid_pos` (logical cell, updated immediately on a move), `current_pixel_pos` (render position relative to grid origin, animates toward `grid_pos`), `image_rect` (slice of the puzzle image). `number == 0` is the empty slot.
  - `Button` — simple hover/click rect.
  - `SlidingPuzzle` — game state + loop: `init_puzzle` → `shuffle_puzzle` (random valid moves), `swap_tiles`, `handle_click` / `handle_key`, `update` (animation + win check), `draw`, `run`.
- `tests/test_sliding_puzzle.py` — pytest suite: shuffle validity/solvability, win detection, click and arrow-key moves. Shares one `SlidingPuzzle` per module (image generation is slow) and resets via `init_puzzle()` / a `set_board()` helper.

## Gotchas

- Positions are `[x, y]` = `[col, row]` lists; compared with `==` against lists, so convert tuples with `list(...)`.
- Game logic must only read `grid_pos`/`empty_pos`; pixel positions are purely visual. `shuffle_puzzle` swaps many times with no animation in between, then `init_puzzle` snaps tiles to the grid. Input is ignored while `self.animating`.
- Click hit-testing mirrors `draw()`: tiles start `GRID_MARGIN` inside `grid_offset`, and clicks in the gaps are ignored.
- The puzzle image is generated procedurally per-pixel in `load_puzzle_image` (slow-ish, runs once at startup).
- Changing `grid_size` beyond 4 requires adjusting `WINDOW_WIDTH/HEIGHT` or `TILE_SIZE`.
- Arrow keys move the tile *into* the empty space (e.g. Up slides the tile below the gap upward).
