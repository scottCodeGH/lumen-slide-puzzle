# CLAUDE.md

Sliding tile puzzle (4x4 by default) in Python + Pygame. Single-file app, no build step.

## Commands

```bash
pip install -r requirements.txt   # pygame>=2.5.0
python sliding_puzzle.py          # run the game (needs a display)
python test_logic.py              # "tests" — see caveat below
```

Headless (CI / cloud container): set `SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy` before importing the module. Note `pygame.init()` and font creation run at import time.

## Layout

- `sliding_puzzle.py` — everything: constants (window/tile sizes, colors, fonts) at top, then
  - `Tile` — `grid_pos` (logical cell), `target_pos` (where it's animating to), `current_pixel_pos` (render position, relative to grid origin), `image_rect` (slice of the puzzle image). `number == 0` is the empty slot.
  - `Button` — simple hover/click rect.
  - `SlidingPuzzle` — game state + loop: `init_puzzle` → `shuffle_puzzle` (random valid moves), `swap_tiles`, `handle_click` / `handle_key`, `update` (animation + win check), `draw`, `run`.
- `test_logic.py` — re-implements logic inline and prints; it does **not** import `sliding_puzzle.py`, so it verifies nothing about the real code.

## Gotchas

- Positions are `[x, y]` = `[col, row]` lists; compared with `==` against lists, so convert tuples with `list(...)`.
- `get_tile_at_pos` looks up by `grid_pos`, but `swap_tiles` only sets `target_pos`; `grid_pos` catches up when `Tile.animate()` finishes. Consecutive swaps without animating in between (i.e. `shuffle_puzzle`) therefore read stale state and produce overlapping/duplicate tiles. Any change to move logic must keep these in sync.
- The puzzle image is generated procedurally per-pixel in `load_puzzle_image` (slow-ish, runs once at startup).
- Changing `grid_size` beyond 4 requires adjusting `WINDOW_WIDTH/HEIGHT` or `TILE_SIZE`.
- Arrow keys move the tile *into* the empty space (e.g. Up slides the tile below the gap upward).
