from __future__ import annotations
import pygame
import typing
from .component import CTComponent
from cuto.style import WindowStyle

if typing.TYPE_CHECKING:
    from cuto.window import CTWindow


class CTToggle(CTComponent):
    def __init__(
        self, text: str, on_toggle_callback: callable, initial_state=False
    ) -> None:
        super().__init__()
        self.font = WindowStyle.main_font
        self.text = text
        self.tag = "toggle"
        self.state = initial_state
        self.callback = on_toggle_callback

    def toggle(self):
        self.state = not self.state
        self.callback(self.state)

    def build(self, window: CTWindow):
        color = WindowStyle.toggle_color_off
        if self.state:
            color = WindowStyle.toggle_color_on
        self.text_surface = self.font.render(
            self.text,
            True,
            color,
            wraplength=window.surface.get_width() - 50,
        )
        surface_size = pygame.Vector2(self.text_surface.get_size()) + pygame.Vector2(
            WindowStyle.padx * 2, WindowStyle.pady * 2
        )
        surface_size.x = window.surface.get_width() - WindowStyle.inter_space * 2
        self.surface = pygame.Surface(surface_size)
        self.surface.fill(WindowStyle.background_color)
        self.surface.blit(
            self.text_surface,
            self.text_surface.get_rect(
                centery=self.surface.get_rect().centery, left=WindowStyle.padx
            ),
        )
        pygame.draw.circle(
            self.surface,
            [50, 50, 50],
            [self.surface.get_rect().right - 20, self.surface.get_rect().centery],
            8,
            0,
        )
        pygame.draw.circle(
            self.surface,
            color,
            [self.surface.get_rect().right - 20, self.surface.get_rect().centery],
            4,
            0,
        )
        self.border(color)

    def border(self, color):
        pygame.draw.rect(self.surface, color, self.surface.get_rect(), 1)
