from __future__ import annotations
import enum
import typing

from cuto.component.text import CTText
from cuto.style.style import WindowStyle
from cuto.component import CTImage
from cuto.window import CTWindow

if typing.TYPE_CHECKING:
    from cuto.component import CTComponent
from cuto.window import couple

import pygame
import cuto.broker as broker

"move it to another file later"


class Cursor:
    def set(cursor: MouseCursor):
        pygame.mouse.set_system_cursor(cursor)

    @classmethod
    def pos(self):
        return pygame.Vector2(pygame.mouse.get_pos())

    @classmethod
    def rel_pos_win(self, win: CTWindow):
        return Cursor.pos() - win.rect.topleft

    @classmethod
    def rel_pos_rect(self, rect: pygame.Rect):
        return Cursor.pos() - rect.topleft


class MouseCursor(enum.IntEnum):
    RESET = 0
    VRES = 6
    HRES = 7
    MOVE = 9


class CTEvent(enum.Enum):
    DRAGBEGIN = 0
    DRAGMOTION = 1
    DRAGSTOP = 2


class WinStatus(enum.Enum):
    """States related to windows, such as resizing and dragging."""

    HANDLE = 0
    RIGHTRESIZE = 1
    TOPRESIZE = 2
    BOTTOMRESIZE = 3
    LEFTRESIZE = 4


class DragMotion:
    def __init__(self) -> None:
        self.begin_pos: typing.Optional[pygame.Vector2] = None
        self.button = 0
        self.started = False
        self.end_pos: typing.Optional[pygame.Vector2] = None
        self.pos: typing.Optional[pygame.Vector2] = None
        self.rel: typing.Optional[list] = None
        self.win_status = None


class CTManager:

    def __init__(self) -> None:
        print(f"[Cuto] Using {WindowStyle.font_name} as main font.")

        self.windows: list[CTWindow] = []
        self.event: list[typing.Optional[pygame.Event]] = []
        self.broker: broker.Broker = broker.Broker()
        self._show = True
        self._internal_win_sep = 50
        self.broker.subscribe(
            pygame.TEXTINPUT,
            lambda data: print(data),
        )
        self.broker.subscribe(
            pygame.MOUSEBUTTONDOWN,
            lambda data: self.on_mouse_click(data),
        )
        self.broker.subscribe(
            pygame.MOUSEBUTTONDOWN,
            lambda data: self.begin_drag(data),
        )
        self.broker.subscribe(
            pygame.KEYDOWN,
            lambda data: self.on_key_down(data),
        )
        self.broker.subscribe(
            pygame.KEYUP,
            lambda data: self.on_key_up(data),
        )
        self.broker.subscribe(
            pygame.MOUSEMOTION,
            lambda data: self.on_mouse_motion(data),
        )
        self.broker.subscribe(
            pygame.MOUSEMOTION,
            lambda data: self.emit_drag(data),
        )
        self.broker.subscribe(
            pygame.MOUSEBUTTONUP,
            lambda data: self.break_hold(data),
        )
        self.broker.subscribe(
            pygame.MOUSEBUTTONUP,
            lambda data: self.stop_drag(data),
        )
        self.broker.subscribe(
            pygame.MOUSEWHEEL,
            lambda data: self.on_wheel(data),
        )
        self.broker.subscribe(
            CTEvent.DRAGMOTION,
            lambda data: self.on_motion_drag(data),
        )
        self._on_select = False
        self._holding = False
        self.active_window: typing.Optional[CTWindow] = None

        self.drag_motion = DragMotion()
        self.current_hover_component: typing.Optional[CTComponent] = None
        self.blocking_component: typing.Optional[CTComponent] = None
        self.temp_check: typing.Optional[pygame.Rect] = None

    def begin_drag(self, data):
        self.drag_motion.begin_pos = pygame.Vector2(data["pos"])
        self.drag_motion.started = True
        self.drag_motion.button = data["button"]
        self.broker.emit(CTEvent.DRAGBEGIN, data)

    def stop_drag(self, data):
        if data["button"] == self.drag_motion.button and self.drag_motion.started:
            self.drag_motion.end_pos = pygame.Vector2(data["pos"])
            self.drag_motion.started = False
            self.drag_motion.win_status = None
            self.broker.emit(CTEvent.DRAGSTOP, data)

    def emit_drag(self, data):
        if self.drag_motion.started:
            self.drag_motion.pos = data["pos"]
            self.drag_motion.rel = data["rel"]
            self.broker.emit(CTEvent.DRAGMOTION, self.drag_motion)

    def on_motion_drag(self, data: DragMotion):
        if data.win_status == WinStatus.HANDLE:
            self.active_window.rect.left += data.rel[0]
            self.active_window.rect.top += data.rel[1]
        if data.win_status == WinStatus.BOTTOMRESIZE:
            self.active_window.resize(
                self.active_window._win_size + pygame.Vector2(0, data.rel[1])
            )
            self.rearrange_components()
            self.build()

        if data.win_status == WinStatus.LEFTRESIZE:
            self.active_window.resize(
                self.active_window._win_size + pygame.Vector2(-data.rel[0], 0)
            )
            self.active_window.rect.left += data.rel[0]
            self.rearrange_components()
            self.build()

        if data.win_status == WinStatus.RIGHTRESIZE:
            self.active_window.resize(
                self.active_window._win_size + pygame.Vector2(data.rel[0], 0)
            )
            self.rearrange_components()
            self.build()

    def on_wheel(self, data):
        if self.active_window.rect.collidepoint(pygame.mouse.get_pos()):
            self.active_window.components[0].rect.top += data["y"] * 50
            if (
                self.active_window.components[0].rect.top
                >= self.active_window.title_text_rect.bottom + 10
            ):
                self.active_window.components[0].rect.top = (
                    self.active_window.title_text_rect.bottom + 10
                )
            self.rearrange_components()
            self.build()

    def on_mouse_motion(self, data):
        if not self.check_if_mouse_hovers_temp_check() and self.temp_check:
            self.delete_temporary_check()
            self.reset_cursor()
        hover_win: typing.Optional[CTWindow] = None
        for window in self.windows:
            if window.rect.collidepoint(Cursor.pos()):
                hover_win = window
                break
        if hover_win:
            checks = [
                [hover_win.get_bottom_resizer, MouseCursor.VRES],
                [hover_win.get_left_resizer, MouseCursor.HRES],
                [hover_win.get_right_resizer, MouseCursor.HRES],
            ]
            for check in checks:
                if check[0]().collidepoint(Cursor.rel_pos_win(hover_win)):
                    self.store_temporary_check(check[0]())
                    Cursor.set(check[1])

        if self.active_window:
            offset_point = self.global_to_window_coord(data["pos"])
            if not self.current_hover_component:
                for component in self.active_window.components:
                    if component.rect.collidepoint(offset_point):
                        pygame.mouse.set_system_cursor(11)
                        self.current_hover_component = component
                        break
            else:
                if not self.current_hover_component.rect.collidepoint(offset_point):
                    self.reset_cursor()
                    self.current_hover_component = None

        if self._holding and self._on_select:
            if data["buttons"][0] == 1:
                self.active_window.rect.left += data["rel"][0]
                self.active_window.rect.top += data["rel"][1]

    def on_key_down(self, data):
        if data["key"] == pygame.K_LCTRL:
            self._on_select = True

    def on_key_up(self, data):
        if data["key"] == pygame.K_LCTRL:
            self._on_select = False

    # change name later wtf is this
    def rearrange_components(self):
        for idx, component in enumerate(self.active_window.components):
            if not component.surface:
                continue
            if idx > 0:
                component.rect.size = component.surface.get_size()
                component.rect.top = (
                    self.active_window.components[idx - 1].rect.bottom
                    + WindowStyle.inter_space
                )
                component.rect.left = WindowStyle.inter_space  # margin

    def is_mouse_on_component(self): ...
    def build(self, _couple=False):
        for window in self.windows:
            window.build()

    def reset_cursor(self):
        Cursor.set(MouseCursor.RESET)

    def break_hold(self, data):
        self._holding = False
        print(self.check_if_mouse_hovers_temp_check())
        if self.check_if_mouse_hovers_temp_check():
            self.delete_temporary_check()
            return
        self.reset_cursor()

    @property
    def internal_win_sep(self):
        return self._internal_win_sep

    @internal_win_sep.setter
    def internal_win_sep(self, value):
        self._internal_win_sep = value

    def grant_active(self, window: CTWindow):
        self.active_window = window

    def global_to_window_coord(self, pos):
        return pygame.Vector2(pos) - self.active_window.rect.topleft

    def check_if_mouse_hovers_temp_check(self):
        if not self.temp_check:
            return False
        return self.temp_check.collidepoint(Cursor.rel_pos_rect(self.temp_check))

    def store_temporary_check(self, rect: pygame.Rect):
        print("storing check")
        self.temp_check = rect

    def delete_temporary_check(self):
        self.temp_check = None

    def on_mouse_click(self, data):
        active_candidates: list[CTWindow] = []
        if data["button"] in [1, 4, 5]:
            for window in self.windows:
                if window.rect.collidepoint(data["pos"]):
                    active_candidates.append(window)
        if self.blocking_component:
            if not self.blocking_component.rect.collidepoint(
                self.global_to_window_coord(data["pos"])
            ):
                self.blocking_component = None

        if len(active_candidates) == 1:
            self.grant_active(active_candidates[0])
            offset_point = self.global_to_window_coord(data["pos"])
            if self.active_window.get_handle_rect().collidepoint(offset_point):
                self.drag_motion.win_status = WinStatus.HANDLE
                Cursor.set(MouseCursor.MOVE)
            if self.active_window.get_bottom_resizer().collidepoint(offset_point):
                self.drag_motion.win_status = WinStatus.BOTTOMRESIZE
            if self.active_window.get_left_resizer().collidepoint(offset_point):
                self.drag_motion.win_status = WinStatus.LEFTRESIZE
                Cursor.set(MouseCursor.HRES)

            if self.active_window.get_right_resizer().collidepoint(offset_point):
                self.drag_motion.win_status = WinStatus.RIGHTRESIZE
                Cursor.set(MouseCursor.HRES)

            for component in self.active_window.components:
                if component.rect.collidepoint(offset_point):
                    if component.tag == "button":
                        component.callback()
                        self.store_temporary_check(component.rect)
                    if component.tag == "toggle":
                        component.toggle()
                        component.needs_rebuild = True
                        self.active_window.build()
                        self.store_temporary_check(component.rect)

                    if component.tag == "listbox":
                        if self.blocking_component:
                            self.blocking_component = None
                        else:
                            self.blocking_component = component
                        self.store_temporary_check(component.rect)

                    if component.tag == "image":
                        couple(
                            CTWindow(self, [400, 400], component.img_path),
                            CTText(f"new window instance id: {CTWindow.win_num}"),
                            CTImage(component.img_path, [380, 380]),
                        )
                        self.build()
                        self.store_temporary_check(component.rect)

                    break

            self._holding = True
            if self._on_select:
                pygame.mouse.set_system_cursor(9)

    def add_window(self, window: CTWindow):
        if type(window).win_num > 1:
            window.rect.top = self.windows[-1].rect.bottom + self._internal_win_sep
        self.windows.append(window)

    def pump_event(self, event: pygame.Event):
        self.broker.emit(event.type, event.dict)

    def render(self, surface: pygame.Surface):
        if not self._show:
            return
        for window in self.windows:
            surface.blit(window.surface, window.rect)
            pygame.draw.rect(
                surface,
                WindowStyle.window_border_color,
                window.surface.get_rect(
                    size=[
                        window.surface.get_width() + 2,
                        window.surface.get_height() + 2,
                    ],
                    topleft=[window.rect.left - 2, window.rect.top - 2],
                ),
                2,
            )
        if self.blocking_component:
            if self.blocking_component.tag == "listbox":
                surface.blit(
                    self.blocking_component.items_surface,
                    self.blocking_component.items_surface.get_rect(
                        top=self.blocking_component.rect.bottom
                        + self.active_window.rect.top,
                        left=self.blocking_component.rect.left
                        + self.active_window.rect.left,
                    ),
                )
        if self._on_select:
            pygame.draw.rect(surface, [100, 100, 100], surface.get_rect(), 2)
            surface.blit(WindowStyle.main_font.render("meow", True, "green"), [10, 10])
