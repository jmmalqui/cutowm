import pygame


class Broker:
    def __init__(self) -> None:
        self.event_dict: dict["str", list[callable]] = {}

    def subscribe(self, event_name, callback):
        if event_name in self.event_dict:
            self.event_dict[event_name].append(callback)
        else:
            self.event_dict[event_name] = [callback]

    def emit(self, event_name, data):
        if event_name in self.event_dict:
            for callback in self.event_dict[event_name]:

                response = callback(data)

    def unsubscribe(self, event_name):
        self.event_dict.pop(event_name)
