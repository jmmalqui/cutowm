import pygame


class WindowStyle:
    """The default style is based on the GruvBox color palette"""

    pygame.init()
    font_name = "ubuntu"
    main_font = pygame.font.SysFont(font_name, 12, True)
    content_font = pygame.font.SysFont(font_name, 12)
    text_color = "#fbf1f7"
    content_color = "#fbf1c7"
    background_color = "#242424"
    border_color = "#33202f"

    button_text_color = "#458588"
    button_background_color = "#458588"
    button_border_color = "#83a598"

    window_background_color = "#282828"
    window_border_color = [50, 50, 50]

    toggle_color_off = "#fb4934"
    toggle_color_on = "#b8bb26"

    padx = 5
    pady = 5
    inter_space = 2
