from __future__ import annotations
import os
import typing
import pygame


if typing.TYPE_CHECKING:
    from cuto.window import CTWindow
from cuto.style import WindowStyle


class CTComponent:
    def __init__(self) -> None:
        self.window: typing.Optional[CTWindow] = None
        self.surface: typing.Optional[pygame.Surface] = None
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.needs_rebuild = True
        self.tag = None

    def border(self):
        if self.surface:
            pygame.draw.rect(self.surface, [100, 100, 100], self.surface.get_rect(), 1)

    def build(self, window: CTWindow): ...
