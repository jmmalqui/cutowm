from __future__ import annotations
import typing

from cuto.style.style import WindowStyle

if typing.TYPE_CHECKING:
    from .window import CTWindow
    from cuto.component import CTComponent


def couple(window: CTWindow, *components: CTComponent):
    for idx, component in enumerate(components):
        component.build(window)
        if not component.surface:
            continue
        if idx == 0:
            component.rect.size = component.surface.get_size()
            component.rect.top = window.title_text_rect.bottom + WindowStyle.inter_space
            component.rect.left = WindowStyle.inter_space  # margin
        else:
            component.rect.size = component.surface.get_size()
            component.rect.top = (
                components[idx - 1].rect.bottom + WindowStyle.inter_space
            )
            component.rect.left = WindowStyle.inter_space  # margin

        window.components.append(component)
        component.window = window
