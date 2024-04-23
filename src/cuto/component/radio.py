from .component import CTComponent


class CTRadio(CTComponent):
    def __init__(self) -> None:
        super().__init__()
        self.tag = "radio"
