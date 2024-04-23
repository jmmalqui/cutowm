from __future__ import annotations
import typing
import pygame

if typing.TYPE_CHECKING:
    from cuto.component import CTComponent
    from cuto.manager import CTManager
from cuto.style import WindowStyle

from pygame.draw import rect


class CTWindow:
    win_num = 0

    def __init__(self, manager: CTManager, win_size: list, win_title: str) -> None:
        CTWindow.win_num += 1

        self.manager: CTManager = manager
        self.components: list[CTComponent] = []

        self._win_size: list[int | float] = win_size
        self._win_title: str = win_title

        self._background_color = WindowStyle.window_background_color
        self._border_color = [30, 30, 30]
        self._text_color = WindowStyle.text_color

        self.rect = pygame.Rect(
            self.manager._internal_win_sep,
            self.manager._internal_win_sep,
            *self._win_size,
        )

        self._id = self.win_num  # Never Changes
        self._z_index = self.win_num  # Changes

        self.title_text = WindowStyle.main_font.render(
            self._win_title, True, self._text_color
        )

        self.surface = pygame.Surface(self._win_size)
        self.title_text_rect = self.get_title_only_text_rect()

        self.surface.fill(self._background_color)
        rect(self.surface, self._border_color, self.surface.get_rect(), 1)
        self.surface.blit(
            self.title_text,
            self.title_text_rect,
        )

        self.manager.add_window(self)

    def get_title_only_text_rect(self):
        return self.title_text.get_rect(
            centerx=self.surface.get_width() // 2,
            centery=(self.title_text.get_height() // 2) + 1,
        )

    def get_handle_rect(self):
        return self.surface.get_rect(height=self.title_text_rect.height + 2)

    def get_left_resizer(self):
        return self.surface.get_rect(width=10)

    def get_right_resizer(self):
        surf_rect = self.surface.get_rect()
        return self.surface.get_rect(width=10, right=surf_rect.right)

    def get_bottom_resizer(self):
        surf_rect = self.surface.get_rect()
        return self.surface.get_rect(height=10, bottom=surf_rect.bottom)

    def resize(self, size):
        self.surface = pygame.Surface(self._win_size)
        self._win_size = size
        self.title_text_rect = self.get_title_only_text_rect()
        self.build(complete_rebuild=True)  # very slow fix later
        self.rect.size = self._win_size

    def build(self, _couple=False, complete_rebuild=False):
        self.surface.fill(self._background_color)
        rect(self.surface, self._border_color, self.surface.get_rect(), 1)

        for component in self.components:
            if component.needs_rebuild:
                component.build(self)
                component.needs_rebuild = False

            if complete_rebuild:
                if component.tag == "image":  # dirty fix later
                    continue
                component.build(self)

            self.surface.blit(component.surface, component.rect)

        rect(
            self.surface,
            self._border_color,
            self.get_handle_rect(),
            0,
        )
        self.surface.blit(
            self.title_text,
            self.title_text_rect,
        )

    # these two would probably be deleted after

    @property
    def background_color(self):
        return self._background_color

    @background_color.setter
    def background_color(self, color: pygame.Color):
        self._background_color = color
