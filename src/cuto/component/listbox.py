from __future__ import annotations
import pygame
import typing

from .component import CTComponent
from cuto.style import WindowStyle

if typing.TYPE_CHECKING:
    from cuto.window import CTWindow


class CTListBox(CTComponent):
    def __init__(self, items: list[str], placeholder: str, description: str) -> None:
        super().__init__()
        self.font = WindowStyle.main_font
        self.tag = "listbox"
        self.items = items
        self.placeholder = placeholder
        self.description = description
        self.items_surface: typing.Optional[pygame.Surface] = None

    def build(self, window: CTWindow):
        self.description_surface = self.font.render(
            self.description,
            True,
            WindowStyle.text_color,
            wraplength=window.surface.get_width() - 20,
        )
        surface_size = pygame.Vector2(
            self.description_surface.get_size()
        ) + pygame.Vector2(WindowStyle.padx * 2, WindowStyle.pady * 2)
        surface_size.x = window.surface.get_width() - WindowStyle.inter_space * 2
        self.surface = pygame.Surface(surface_size)
        self.surface.fill(WindowStyle.background_color)
        self.surface.blit(
            self.description_surface,
            self.description_surface.get_rect(
                centery=self.surface.get_rect().centery, left=WindowStyle.padx
            ),
        )
        item_labels = []
        for item in self.items:
            surf = self.font.render(
                item,
                True,
                WindowStyle.text_color,
                wraplength=self.surface.get_width() - 20,
            )
            item_labels.append(
                [
                    surf,
                    surf.get_rect(
                        height=surf.get_height() + WindowStyle.pady * 2,
                    ),
                ]
            )
        # change later so it only shows n items defined by the user
        items_surface = pygame.Surface(
            [
                self.surface.get_width(),
                sum([item[1].height for item in item_labels]),
            ]
        )
        items_surface.fill([20, 20, 20])
        for idx, item in enumerate(item_labels):
            if idx > 0:
                item[1].top = item_labels[idx - 1][1].bottom
            item_rect = item[1].copy()
            item_rect.height = item[0].get_height()
            item_rect.centery = item[1].centery
            item_rect.left = WindowStyle.padx
            items_surface.blit(item[0], item_rect)
        self.items_surface = items_surface
        self.border()
