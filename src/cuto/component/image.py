from __future__ import annotations
import os
import pygame
import pygame
import typing

from cuto.style import WindowStyle
from .component import CTComponent

if typing.TYPE_CHECKING:
    from cuto.window import CTWindow


def fit_box(box, to_be_fit):
    box_x = box[0]
    box_y = box[1]
    img_x = to_be_fit[0]
    img_y = to_be_fit[1]

    if img_x * box_y / img_y < box_x:
        return [img_x * box_y / img_y, box_y]
    else:
        return [box_x, img_y * box_x / img_x]


class CTImage(CTComponent):
    def __init__(self, img_path: str, size: list = [60, 60]) -> None:
        super().__init__()
        self.img_path = img_path
        self.size = size
        self.tag = "image"

    def build(self, window: CTWindow):
        self.window = window
        if os.path.splitext(self.img_path)[1].lower() not in [".jpg", ".png", ".jpeg"]:
            self.surface = pygame.Surface(self.size)
            self.surface.fill("violet")
        else:
            self.surface = pygame.Surface(self.size)
            self.surface.fill(WindowStyle.background_color)
            self.image = pygame.image.load(self.img_path).convert_alpha()
            self.image = pygame.transform.smoothscale(
                self.image, fit_box(self.size, self.image.get_size())
            )
            self.surface.blit(
                self.image, self.image.get_rect(center=self.surface.get_rect().center)
            )
            print("resizing", self.needs_rebuild)
        self.border()
