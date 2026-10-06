import pygame
import random

LANES = 4
LANE_KEYS = [pygame.K_d, pygame.K_f, pygame.K_j, pygame.K_k]
LANE_LABELS = ['D', 'F', 'J', 'K']
LANE_COLORS = [
    (220, 80, 80),
    (80, 180, 220),
    (100, 220, 100),
    (220, 180, 60)
]


class Note:
    WIDTH = 70
    HEIGHT = 20

    def __init__(
        self,
        lane,
        y=-30,
        speed=4,
        is_hold=False,
        hold_duration=1000
    ):
        self.lane = lane
        self.y = y
        self.speed = speed

        self.hit = False
        self.missed = False

        # Hold-note properties
        self.is_hold = is_hold
        self.hold_duration = hold_duration
        self.holding = False
        self.hold_start_time = 0

    def update(self):
        self.y += self.speed

    def get_rect(self, lane_x):
        if self.is_hold:
            # Make the note visually long enough to represent
            # the required 1-second hold.
            hold_height = max(
                self.HEIGHT,
                int(self.speed * 60 * (self.hold_duration / 1000))
            )

            return pygame.Rect(
                lane_x - self.WIDTH // 2,
                int(self.y),
                self.WIDTH,
                hold_height
            )

        return pygame.Rect(
            lane_x - self.WIDTH // 2,
            int(self.y),
            self.WIDTH,
            self.HEIGHT
        )