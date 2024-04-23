from __future__ import annotations
import pygame
import typing
from cuto.style import WindowStyle
from .component import CTComponent

if typing.TYPE_CHECKING:
    from cuto.window import CTWindow


class CTButton(CTComponent):
    def __init__(self, text: str, callback: callable) -> None:
        super().__init__()
        self.font = WindowStyle.main_font
        self.text = text
        self.callback = callback
        self.tag = "button"

    def build(self, window: CTWindow):
        self.window = window
        self.text_surface = self.font.render(self.text, True, WindowStyle.text_color)

        self.surface = pygame.Surface(
            pygame.Vector2(self.text_surface.get_size())
            + pygame.Vector2(WindowStyle.padx * 2, WindowStyle.pady * 2)
        )
        self.surface.fill(WindowStyle.button_background_color)
        pygame.draw.rect(
            self.surface,
            WindowStyle.button_background_color,
            self.surface.get_rect(),
            2,
        )
        self.surface.blit(
            self.text_surface,
            self.text_surface.get_rect(center=self.surface.get_rect().center),
        )
