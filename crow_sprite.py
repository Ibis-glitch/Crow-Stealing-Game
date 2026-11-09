"""Animated hand-drawn crow for The Crow Job.

Put this file next to entities.py and put crow_idle_strip.png in assets/.
The crow's collision rectangle is NOT changed by this module.
"""
from pathlib import Path
import pygame


class CrowSprite:
    FRAME_COUNT = 12
    FRAME_DURATION_MS = 180  # 12 frames = ~2.2 seconds per breath

    def __init__(self, width=24):
        asset_path = Path(__file__).resolve().parent / "assets" / "crow_idle_strip.png"
        sheet = pygame.image.load(str(asset_path)).convert_alpha()

        frame_width = sheet.get_width() // self.FRAME_COUNT
        frame_height = sheet.get_height()
        draw_height = max(1, round(width * frame_height / frame_width))
        draw_size = (width, draw_height)

        self.right_frames = []
        self.left_frames = []
        for i in range(self.FRAME_COUNT):
            source_rect = pygame.Rect(i * frame_width, 0, frame_width, frame_height)
            source_image = sheet.subsurface(source_rect)
            image = pygame.transform.smoothscale(source_image, draw_size)
            self.right_frames.append(image)
            self.left_frames.append(pygame.transform.flip(image, True, False))

        self.started_ms = pygame.time.get_ticks()

    def draw(self, surface, hitbox, facing=(1, 0), idle=True):
        """Draw the crow in world coordinates. The feet align to hitbox.bottom."""
        if idle:
            elapsed = pygame.time.get_ticks() - self.started_ms
            frame_index = (elapsed // self.FRAME_DURATION_MS) % self.FRAME_COUNT
        else:
            frame_index = 0

        frames = self.left_frames if facing[0] < 0 else self.right_frames
        image = frames[frame_index]
        destination = image.get_rect(midbottom=hitbox.midbottom)
        surface.blit(image, destination)
