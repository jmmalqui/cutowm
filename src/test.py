import itertools
import os
import pygame
import cuto
import operator


def use_state(val):
    return val, lambda a: operator.methodcaller()


def toggle_var(cls, var_name: str):
    return lambda state: setattr(cls, var_name, state)


class Game:
    def __init__(self) -> None:
        pygame.init()
        self.clock = pygame.Clock()
        self.display = pygame.display.set_mode([1920 / 2, 1080 / 2], pygame.RESIZABLE)
        self.winman = cuto.CTManager()
        self.show_bg = True
        self.somewindow = cuto.CTWindow(self.winman, [320, 220], "Cuto window")
        cuto.couple(
            self.somewindow,
            cuto.CTButton("Button", lambda: print("button pressed")),
            cuto.CTToggle(
                "Show Background Image",
                toggle_var(self, "show_bg"),
                self.show_bg,
            ),
            cuto.CTListBox(
                [
                    "Option 1",
                    "Option 2",
                ],
                "Name",
                "Choose",
            ),
            cuto.CTImage("res/testimg.jpg", [120, 120]),
        ),

        self.winman.build()
        self.running = True

    def check_events(self):
        for event in pygame.event.get():
            self.winman.pump_event(event)
            if event.type == pygame.QUIT:
                self.running = False

    def update(self): ...
    def render(self):
        self.display.fill("black")
        self.winman.render(self.display)
        pygame.display.flip()

    def run(self):
        while self.running:
            self.clock.tick()
            pygame.display.set_caption(f"{self.clock.get_fps() :.0f}")
            self.check_events()
            self.update()
            self.render()


if __name__ == "__main__":
    g = Game()
    g.run()
