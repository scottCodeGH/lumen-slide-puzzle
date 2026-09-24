import random

import pygame
import pytest

import sliding_puzzle as sp


@pytest.fixture(scope="module")
def game():
    # Building the puzzle image is slow, so share one game and re-init per test.
    return sp.SlidingPuzzle(grid_size=4)


@pytest.fixture
def fresh(game):
    random.seed(0)
    game.init_puzzle()
    return game


def board(game):
    """Map of (x, y) -> tile number."""
    return {tuple(t.grid_pos): t.number for t in game.tiles}


def set_board(game, layout):
    """Place tiles from a row-major list of numbers (0 = empty)."""
    by_number = {t.number: t for t in game.tiles}
    for i, number in enumerate(layout):
        tile = by_number[number]
        tile.grid_pos = [i % game.grid_size, i // game.grid_size]
        tile.snap_to_grid()
        if number == 0:
            game.empty_pos = list(tile.grid_pos)
    game.moves = 0
    game.game_won = False
    game.animating = False


def solved_layout(n):
    return list(range(1, n * n)) + [0]


def is_solvable(game):
    n = game.grid_size
    cells = board(game)
    order = [cells[(x, y)] for y in range(n) for x in range(n)]
    nums = [v for v in order if v != 0]
    inversions = sum(1 for i in range(len(nums)) for j in range(i + 1, len(nums)) if nums[i] > nums[j])
    if n % 2 == 1:
        return inversions % 2 == 0
    empty_row_from_bottom = n - game.empty_pos[1]
    return (inversions + empty_row_from_bottom) % 2 == 1


def tile_center(game, pos):
    """Screen coordinates of the centre of the cell at grid pos, matching draw()."""
    step = sp.TILE_SIZE + sp.GRID_MARGIN
    x = game.grid_offset[0] + sp.GRID_MARGIN + pos[0] * step + sp.TILE_SIZE // 2
    y = game.grid_offset[1] + sp.GRID_MARGIN + pos[1] * step + sp.TILE_SIZE // 2
    return x, y


@pytest.mark.parametrize("seed", range(50))
def test_shuffle_is_valid_permutation(game, seed):
    random.seed(seed)
    game.init_puzzle()
    n = game.grid_size
    cells = board(game)
    assert set(cells) == {(x, y) for x in range(n) for y in range(n)}
    assert sorted(cells.values()) == list(range(n * n))
    assert cells[tuple(game.empty_pos)] == 0


@pytest.mark.parametrize("seed", range(50))
def test_shuffle_is_solvable_and_scrambled(game, seed):
    random.seed(seed)
    game.init_puzzle()
    assert is_solvable(game)
    assert not game.check_win_condition()
    assert game.moves == 0
    assert not any(t.is_animating() for t in game.tiles)


def test_solved_board_detected(fresh):
    set_board(fresh, solved_layout(4))
    assert fresh.check_win_condition()


def test_win_detected_after_final_move(fresh):
    layout = solved_layout(4)
    layout[-2], layout[-1] = layout[-1], layout[-2]  # 15 and empty swapped
    set_board(fresh, layout)
    assert not fresh.check_win_condition()

    fresh.swap_tiles((3, 3))
    assert fresh.moves == 1
    for _ in range(200):
        fresh.update()
    assert fresh.game_won


def test_click_moves_adjacent_tile(fresh):
    set_board(fresh, solved_layout(4))
    fresh.handle_click(tile_center(fresh, (3, 2)))
    cells = board(fresh)
    assert cells[(3, 3)] == 12
    assert cells[(3, 2)] == 0
    assert fresh.moves == 1


def test_click_on_non_adjacent_tile_does_nothing(fresh):
    set_board(fresh, solved_layout(4))
    before = board(fresh)
    fresh.handle_click(tile_center(fresh, (0, 0)))
    fresh.handle_click(tile_center(fresh, (2, 2)))  # diagonal
    assert board(fresh) == before
    assert fresh.moves == 0


def test_click_hit_testing_accounts_for_margin(fresh):
    set_board(fresh, solved_layout(4))
    step = sp.TILE_SIZE + sp.GRID_MARGIN
    # Last pixels of the tile at (3, 2), just above the gap: should move it.
    x = fresh.grid_offset[0] + sp.GRID_MARGIN + 3 * step + 5
    y = fresh.grid_offset[1] + sp.GRID_MARGIN + 2 * step + sp.TILE_SIZE - 1
    fresh.handle_click((x, y))
    assert board(fresh)[(3, 3)] == 12


def test_click_in_gap_does_nothing(fresh):
    set_board(fresh, solved_layout(4))
    step = sp.TILE_SIZE + sp.GRID_MARGIN
    x = fresh.grid_offset[0] + sp.GRID_MARGIN + 3 * step + 5
    y = fresh.grid_offset[1] + sp.GRID_MARGIN + 2 * step + sp.TILE_SIZE + 2
    fresh.handle_click((x, y))
    assert fresh.moves == 0


@pytest.mark.parametrize(
    "key, moved_from",
    [(pygame.K_DOWN, (1, 0)), (pygame.K_RIGHT, (0, 1)), (pygame.K_UP, (1, 2)), (pygame.K_LEFT, (2, 1))],
)
def test_arrow_keys_move_adjacent_tile(fresh, key, moved_from):
    layout = solved_layout(4)
    # Put the empty cell in the middle at (1, 1), where tile 6 normally sits.
    layout[5], layout[15] = 0, 6
    set_board(fresh, layout)
    number = board(fresh)[moved_from]

    fresh.handle_key(key)

    cells = board(fresh)
    assert cells[(1, 1)] == number
    assert cells[moved_from] == 0
    assert fresh.moves == 1


def test_arrow_key_at_edge_does_nothing(fresh):
    set_board(fresh, solved_layout(4))  # empty at bottom-right corner
    before = board(fresh)
    fresh.handle_key(pygame.K_UP)  # no tile below the empty cell
    fresh.handle_key(pygame.K_LEFT)  # no tile to the right
    assert board(fresh) == before
    assert fresh.moves == 0


def test_input_ignored_while_animating(fresh):
    set_board(fresh, solved_layout(4))
    fresh.handle_key(pygame.K_DOWN)
    assert fresh.animating
    fresh.handle_key(pygame.K_DOWN)
    assert fresh.moves == 1
    for _ in range(200):
        fresh.update()
    assert not fresh.animating
