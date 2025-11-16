#!/usr/bin/env python3
"""
Sliding Tile Puzzle Game
A beautiful and polished puzzle game using Python and Pygame.
"""

import pygame
import random
import sys
import time
from typing import List, Tuple, Optional

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 700
GRID_SIZE = 4  # 4x4 puzzle (can be changed to 3 for easier mode)
TILE_SIZE = 120
GRID_MARGIN = 10
ANIMATION_SPEED = 15  # Higher = faster animation

# Colors
BG_COLOR = (240, 248, 255)  # Alice blue
GRID_BG_COLOR = (70, 130, 180)  # Steel blue
TILE_BORDER_COLOR = (255, 255, 255)
TEXT_COLOR = (25, 25, 112)  # Midnight blue
BUTTON_COLOR = (100, 149, 237)  # Cornflower blue
BUTTON_HOVER_COLOR = (65, 105, 225)  # Royal blue
BUTTON_TEXT_COLOR = (255, 255, 255)
WIN_OVERLAY_COLOR = (0, 0, 0, 180)  # Semi-transparent black

# Fonts
TITLE_FONT = pygame.font.Font(None, 48)
UI_FONT = pygame.font.Font(None, 32)
WIN_FONT = pygame.font.Font(None, 64)
BUTTON_FONT = pygame.font.Font(None, 28)


class Tile:
    """Represents a single puzzle tile."""

    def __init__(self, number: int, pos: Tuple[int, int], image_rect: pygame.Rect):
        self.number = number  # 0 represents empty tile
        self.grid_pos = list(pos)  # Current position in grid
        self.target_pos = list(pos)  # Target position for animation
        self.current_pixel_pos = [0, 0]  # Current pixel position for smooth animation
        self.image_rect = image_rect  # The portion of the image this tile shows

    def update_position(self, new_pos: Tuple[int, int]):
        """Set a new target position for the tile to animate to."""
        self.target_pos = list(new_pos)

    def animate(self):
        """Smoothly animate tile to target position."""
        target_pixel_x = self.target_pos[0] * (TILE_SIZE + GRID_MARGIN)
        target_pixel_y = self.target_pos[1] * (TILE_SIZE + GRID_MARGIN)

        # Smooth animation
        dx = target_pixel_x - self.current_pixel_pos[0]
        dy = target_pixel_y - self.current_pixel_pos[1]

        if abs(dx) > 1:
            self.current_pixel_pos[0] += dx / ANIMATION_SPEED
        else:
            self.current_pixel_pos[0] = target_pixel_x

        if abs(dy) > 1:
            self.current_pixel_pos[1] += dy / ANIMATION_SPEED
        else:
            self.current_pixel_pos[1] = target_pixel_y

        # Update grid position when animation completes
        if self.current_pixel_pos[0] == target_pixel_x and self.current_pixel_pos[1] == target_pixel_y:
            self.grid_pos = list(self.target_pos)

    def is_animating(self) -> bool:
        """Check if tile is currently animating."""
        return self.grid_pos != self.target_pos


class Button:
    """A clickable button UI element."""

    def __init__(self, rect: pygame.Rect, text: str, color: Tuple[int, int, int],
                 hover_color: Tuple[int, int, int]):
        self.rect = rect
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle mouse events. Returns True if button was clicked."""
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False

    def draw(self, screen: pygame.Surface):
        """Draw the button."""
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        pygame.draw.rect(screen, TILE_BORDER_COLOR, self.rect, 2, border_radius=8)

        text_surface = BUTTON_FONT.render(self.text, True, BUTTON_TEXT_COLOR)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)


class SlidingPuzzle:
    """Main game class for the sliding tile puzzle."""

    def __init__(self, grid_size: int = 4):
        self.grid_size = grid_size
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Sliding Puzzle Game")

        self.clock = pygame.time.Clock()
        self.running = True

        # Game state
        self.tiles: List[Tile] = []
        self.empty_pos = [grid_size - 1, grid_size - 1]  # Position of empty tile
        self.moves = 0
        self.start_time = time.time()
        self.game_won = False
        self.animating = False

        # Load and prepare puzzle image
        self.puzzle_image = self.load_puzzle_image()

        # UI elements
        grid_offset_x = (WINDOW_WIDTH - (TILE_SIZE * grid_size + GRID_MARGIN * (grid_size - 1))) // 2
        grid_offset_y = 120
        self.grid_offset = (grid_offset_x, grid_offset_y)

        self.reset_button = Button(
            pygame.Rect(WINDOW_WIDTH // 2 - 80, WINDOW_HEIGHT - 70, 160, 50),
            "New Game",
            BUTTON_COLOR,
            BUTTON_HOVER_COLOR
        )

        # Initialize puzzle
        self.init_puzzle()

    def load_puzzle_image(self) -> pygame.Surface:
        """Load or create a beautiful puzzle image."""
        # Create a beautiful gradient image with geometric patterns
        image = pygame.Surface((TILE_SIZE * self.grid_size, TILE_SIZE * self.grid_size))

        # Create a beautiful gradient background
        for y in range(TILE_SIZE * self.grid_size):
            for x in range(TILE_SIZE * self.grid_size):
                # Create a radial gradient effect
                center_x = TILE_SIZE * self.grid_size // 2
                center_y = TILE_SIZE * self.grid_size // 2
                distance = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
                max_distance = ((center_x) ** 2 + (center_y) ** 2) ** 0.5

                # Color gradient from blue to purple
                ratio = distance / max_distance
                r = int(100 + 120 * ratio)
                g = int(50 + 100 * (1 - ratio))
                b = int(200 - 50 * ratio)

                image.set_at((x, y), (r, g, b))

        # Add decorative circles
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                center_x = i * TILE_SIZE + TILE_SIZE // 2
                center_y = j * TILE_SIZE + TILE_SIZE // 2
                radius = TILE_SIZE // 3

                # Draw decorative circle
                pygame.draw.circle(image, (255, 255, 255, 30), (center_x, center_y), radius, 3)
                pygame.draw.circle(image, (255, 255, 255, 50), (center_x, center_y), radius // 2)

                # Draw tile number in the center for visual interest
                number = i + j * self.grid_size + 1
                if number < self.grid_size * self.grid_size:
                    num_font = pygame.font.Font(None, 72)
                    num_surface = num_font.render(str(number), True, (255, 255, 255, 200))
                    num_rect = num_surface.get_rect(center=(center_x, center_y))
                    image.blit(num_surface, num_rect)

        return image

    def init_puzzle(self):
        """Initialize the puzzle with tiles in solved position, then shuffle."""
        self.tiles = []

        # Create tiles in solved position
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                tile_num = row * self.grid_size + col + 1

                # Last tile is empty
                if tile_num == self.grid_size * self.grid_size:
                    tile_num = 0
                    self.empty_pos = [col, row]

                # Define the image portion for this tile
                image_rect = pygame.Rect(
                    col * TILE_SIZE,
                    row * TILE_SIZE,
                    TILE_SIZE,
                    TILE_SIZE
                )

                tile = Tile(tile_num, (col, row), image_rect)
                tile.current_pixel_pos = [col * (TILE_SIZE + GRID_MARGIN),
                                         row * (TILE_SIZE + GRID_MARGIN)]
                self.tiles.append(tile)

        # Shuffle the puzzle
        self.shuffle_puzzle()

        # Reset game state
        self.moves = 0
        self.start_time = time.time()
        self.game_won = False

    def shuffle_puzzle(self, num_moves: int = 100):
        """Shuffle the puzzle using valid moves to ensure solvability."""
        for _ in range(num_moves):
            # Get valid moves
            valid_moves = self.get_valid_moves()
            if valid_moves:
                # Pick a random valid move
                move_pos = random.choice(valid_moves)
                # Swap without counting as a player move
                self.swap_tiles(move_pos, count_move=False)

    def get_valid_moves(self) -> List[Tuple[int, int]]:
        """Get list of tiles that can be moved (adjacent to empty space)."""
        valid_moves = []
        empty_x, empty_y = self.empty_pos

        # Check all four directions
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        for dx, dy in directions:
            new_x, new_y = empty_x + dx, empty_y + dy
            if 0 <= new_x < self.grid_size and 0 <= new_y < self.grid_size:
                valid_moves.append((new_x, new_y))

        return valid_moves

    def get_tile_at_pos(self, pos: Tuple[int, int]) -> Optional[Tile]:
        """Get the tile at a specific grid position."""
        for tile in self.tiles:
            if tile.grid_pos == list(pos):
                return tile
        return None

    def swap_tiles(self, tile_pos: Tuple[int, int], count_move: bool = True):
        """Swap a tile with the empty space."""
        tile = self.get_tile_at_pos(tile_pos)
        if tile and tile.number != 0:
            # Update tile position
            old_pos = tile.grid_pos.copy()
            tile.update_position(tuple(self.empty_pos))

            # Update empty tile position
            empty_tile = self.get_tile_at_pos(tuple(self.empty_pos))
            if empty_tile:
                empty_tile.update_position(tuple(old_pos))

            # Update empty position
            self.empty_pos = list(old_pos)

            # Count move if it's a player move
            if count_move:
                self.moves += 1
                self.animating = True

    def handle_click(self, mouse_pos: Tuple[int, int]):
        """Handle mouse click on the puzzle grid."""
        if self.game_won or self.animating:
            return

        # Convert mouse position to grid position
        grid_x = (mouse_pos[0] - self.grid_offset[0]) // (TILE_SIZE + GRID_MARGIN)
        grid_y = (mouse_pos[1] - self.grid_offset[1]) // (TILE_SIZE + GRID_MARGIN)

        # Check if click is within grid
        if 0 <= grid_x < self.grid_size and 0 <= grid_y < self.grid_size:
            # Check if clicked tile is adjacent to empty space
            if (grid_x, grid_y) in self.get_valid_moves():
                self.swap_tiles((grid_x, grid_y))

    def handle_key(self, key: int):
        """Handle arrow key presses."""
        if self.game_won or self.animating:
            return

        # Arrow keys move the empty space (opposite to tile movement)
        move_map = {
            pygame.K_UP: (0, 1),      # Move empty up = tile below moves up
            pygame.K_DOWN: (0, -1),   # Move empty down = tile above moves down
            pygame.K_LEFT: (1, 0),    # Move empty left = tile right moves left
            pygame.K_RIGHT: (-1, 0)   # Move empty right = tile left moves right
        }

        if key in move_map:
            dx, dy = move_map[key]
            new_x = self.empty_pos[0] + dx
            new_y = self.empty_pos[1] + dy

            if 0 <= new_x < self.grid_size and 0 <= new_y < self.grid_size:
                self.swap_tiles((new_x, new_y))

    def check_win_condition(self) -> bool:
        """Check if the puzzle is solved."""
        for tile in self.tiles:
            expected_x = (tile.number - 1) % self.grid_size if tile.number > 0 else self.grid_size - 1
            expected_y = (tile.number - 1) // self.grid_size if tile.number > 0 else self.grid_size - 1

            if tile.grid_pos != [expected_x, expected_y]:
                return False
        return True

    def update(self):
        """Update game state."""
        # Update tile animations
        any_animating = False
        for tile in self.tiles:
            tile.animate()
            if tile.is_animating():
                any_animating = True

        self.animating = any_animating

        # Check win condition after animations complete
        if not self.animating and not self.game_won and self.moves > 0:
            if self.check_win_condition():
                self.game_won = True

    def draw(self):
        """Draw the game."""
        self.screen.fill(BG_COLOR)

        # Draw title
        title_surface = TITLE_FONT.render("Sliding Puzzle", True, TEXT_COLOR)
        title_rect = title_surface.get_rect(centerx=WINDOW_WIDTH // 2, top=20)
        self.screen.blit(title_surface, title_rect)

        # Draw game info (moves and time)
        elapsed_time = int(time.time() - self.start_time)
        minutes = elapsed_time // 60
        seconds = elapsed_time % 60

        info_text = f"Moves: {self.moves}  |  Time: {minutes:02d}:{seconds:02d}"
        info_surface = UI_FONT.render(info_text, True, TEXT_COLOR)
        info_rect = info_surface.get_rect(centerx=WINDOW_WIDTH // 2, top=75)
        self.screen.blit(info_surface, info_rect)

        # Draw grid background
        grid_bg_rect = pygame.Rect(
            self.grid_offset[0] - GRID_MARGIN,
            self.grid_offset[1] - GRID_MARGIN,
            TILE_SIZE * self.grid_size + GRID_MARGIN * (self.grid_size + 1),
            TILE_SIZE * self.grid_size + GRID_MARGIN * (self.grid_size + 1)
        )
        pygame.draw.rect(self.screen, GRID_BG_COLOR, grid_bg_rect, border_radius=10)

        # Draw tiles
        for tile in self.tiles:
            if tile.number == 0:  # Skip empty tile
                continue

            # Calculate screen position
            screen_x = self.grid_offset[0] + tile.current_pixel_pos[0] + GRID_MARGIN
            screen_y = self.grid_offset[1] + tile.current_pixel_pos[1] + GRID_MARGIN

            # Draw tile background
            tile_rect = pygame.Rect(screen_x, screen_y, TILE_SIZE, TILE_SIZE)

            # Draw the image portion for this tile
            self.screen.blit(self.puzzle_image, tile_rect, tile.image_rect)

            # Draw tile border
            pygame.draw.rect(self.screen, TILE_BORDER_COLOR, tile_rect, 3, border_radius=5)

        # Draw reset button
        self.reset_button.draw(self.screen)

        # Draw win overlay
        if self.game_won:
            # Semi-transparent overlay
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill(WIN_OVERLAY_COLOR)
            self.screen.blit(overlay, (0, 0))

            # Win message
            win_text = "Solved!"
            win_surface = WIN_FONT.render(win_text, True, (255, 215, 0))  # Gold color
            win_rect = win_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))
            self.screen.blit(win_surface, win_rect)

            # Stats
            stats_text = f"Completed in {self.moves} moves!"
            stats_surface = UI_FONT.render(stats_text, True, (255, 255, 255))
            stats_rect = stats_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20))
            self.screen.blit(stats_surface, stats_rect)

            # Prompt to play again
            prompt_text = "Click 'New Game' to play again"
            prompt_surface = UI_FONT.render(prompt_text, True, (200, 200, 200))
            prompt_rect = prompt_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 70))
            self.screen.blit(prompt_surface, prompt_rect)

        pygame.display.flip()

    def run(self):
        """Main game loop."""
        while self.running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        self.handle_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    self.handle_key(event.key)

                # Handle button events
                if self.reset_button.handle_event(event):
                    self.init_puzzle()

            # Update and draw
            self.update()
            self.draw()

            # Cap frame rate
            self.clock.tick(60)

        pygame.quit()
        sys.exit()


def main():
    """Entry point for the game."""
    # You can change GRID_SIZE to 3 for an easier version
    game = SlidingPuzzle(grid_size=4)
    game.run()


if __name__ == "__main__":
    main()
