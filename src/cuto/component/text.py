from __future__ import annotations
import pygame
import typing
from .component import CTComponent
from cuto.style import WindowStyle

if typing.TYPE_CHECKING:
    from cuto.window import CTWindow


class CTText(CTComponent):
    def __init__(
        self,
        text: str,
        font: pygame.Font | str = WindowStyle.main_font,
        color: pygame.Color = WindowStyle.content_color,
        antialias: bool = True,
        bgcolor: typing.Optional[pygame.Color] = None,
    ) -> None:
        super().__init__()
        self.font = font
        self.text = text
        self.antialias = antialias
        self.color = color
        self.bgcolor = bgcolor

    def build(self, window: CTWindow):
        if type(self.font) is pygame.Surface:
            self.surface = self.font.render(
                self.text,
                self.antialias,
                self.color,
                self.bgcolor,
                wraplength=window.surface.get_width() - 20,
            )
