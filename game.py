"""
Game class that handles the game loop and user input.
"""

from dataclasses import dataclass

import pygame
import numpy as np

from renderer import draw_voxels


# Game constants
GAME_TITLE = "PyVoxelSpace"  # Game title
DISTANCE = 1500.  # Maximum distance to draw
DEFAULT_PLAYER_ANGLE = 45.  # Initial player angle
DEFAULT_HORIZON = 150.  # Initial player horizon (vertical angle)
DEFAULT_HEIGHT = 100.  # Initial player height (vertical position)
HEIGHT_SCALE = 400.  # Map height scale factor


@dataclass
class Player:
    """
    Player data class that holds the player's position, angle, horizon and elevation.
    """
    x: float
    y: float
    angle: float
    horizon: float
    elevation: float


class Game:
    """
    Main game class that handles the game loop and user input.
    """
    _map_width: int
    _map_height: int
    _height_buffer: np.ndarray
    _color_buffer: np.ndarray
    _screen_buffer: np.ndarray
    _render_surface: pygame.Surface
    _render_width: int
    _render_height: int
    _hud_image: pygame.Surface

    _clock: pygame.time.Clock
    _font: pygame.font.Font

    player: Player

    def __init__(self, width: int = 800, height: int = 600, render_width: int = 320, render_height: int = 240):
        """
        Initialize the game class.
        :param width: Game window width
        :param height: Game window height
        :param render_width: Render buffer width
        :param render_height: Render buffer height
        """
        self.color_map_image = None
        pygame.init()

        # Create the screen
        self.screen = pygame.display.set_mode((width, height), pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE)

        # Title and Icon
        pygame.display.set_caption(GAME_TITLE)

        # Load resources
        self._load_resources()

        # Initialize game data
        self._render_width = render_width
        self._render_height = render_height
        self._render_surface = pygame.Surface((render_width, render_height))
        self._screen_buffer = np.full((render_width, render_height, 3), (0, 0, 0))
        self._clock = pygame.time.Clock()
        self._font = pygame.sysfont.SysFont("Arial", 18)

        # Initialize player
        self.player = Player(
            x=self._map_width // 2,
            y=self._map_height // 2,
            angle=np.radians(DEFAULT_PLAYER_ANGLE),
            horizon=DEFAULT_HORIZON,
            elevation=DEFAULT_HEIGHT
        )

    def __del__(self):
        pygame.quit()

    def run(self):
        """
        Run the game loop. This method will block until the game is closed.
        """
        dt = 0
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Process user input and update the game state
            self._process_keys(dt)

            # Render voxels
            elevation = draw_voxels(
                out=self._screen_buffer,
                out_w=self._render_width,
                out_h=self._render_height - 74,
                pos_x=self.player.x,
                pos_y=self.player.y,
                angle=self.player.angle,
                horizon=self.player.horizon,
                elevation=self.player.elevation,
                scale=HEIGHT_SCALE,
                distance=DISTANCE,
                height_map=self._height_buffer,
                color_map=self._color_buffer
            )

            # If the player is below the ground, move him up
            if elevation > self.player.elevation - 5.0:
                self.player.elevation = elevation + 5.0

            # Draw the screen buffer to the screen surface and scale it up
            pygame.surfarray.blit_array(self._render_surface, self._screen_buffer)
            self._render_surface.blit(self._hud_image, (0, 0))
            self.screen.blit(
                pygame.transform.scale(self._render_surface, self.screen.get_size()),
                (0, 0, self._render_width, self._render_height)
            )

            # Draw FPS
            fps = self._font.render(str(int(self._clock.get_fps())), True, pygame.Color('white'))
            self.screen.blit(fps, (10, 10))

            # Update the screen and wait for the next frame
            pygame.display.flip()
            dt = self._clock.tick(60)

    def _load_resources(self):
        """
        Load game resources.
        """
        # Load hud image
        self._hud_image = pygame.image.load('assets/hud.png')

        # Load height and color maps as numpy arrays
        height_map_image = pygame.image.load('assets/D1.png')
        self._height_buffer = pygame.surfarray.array3d(height_map_image)
        color_map_image = pygame.image.load('assets/C1W.png')
        self._color_buffer = pygame.surfarray.array3d(color_map_image)

        self._map_width = color_map_image.get_width()
        self._map_height = color_map_image.get_height()

    def _process_keys(self, dt: float):
        """
        Process user input and update the game state.
        :param dt: Time delta
        """
        keys = pygame.key.get_pressed()
        if keys[pygame.K_d]:
            self.player.angle -= 0.001 * dt
        if keys[pygame.K_a]:
            self.player.angle += 0.001 * dt
        if keys[pygame.K_s]:
            self.player.x += np.sin(self.player.angle) * 0.05 * dt
            self.player.y += np.cos(self.player.angle) * 0.05 * dt
        if keys[pygame.K_w]:
            self.player.x -= np.sin(self.player.angle) * 0.05 * dt
            self.player.y -= np.cos(self.player.angle) * 0.05 * dt
        if keys[pygame.K_SPACE]:
            self.player.horizon += 0.1 * dt
        if keys[pygame.K_RSHIFT]:
            self.player.horizon -= 0.1 * dt
        if keys[pygame.K_UP]:
            self.player.elevation += 0.1 * dt
        if keys[pygame.K_DOWN]:
            self.player.elevation -= 0.1 * dt
