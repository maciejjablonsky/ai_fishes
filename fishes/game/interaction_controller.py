import pygame as pg
class EventsController:
    def handle_events(self):
        for event in self.get_events():
            pass


    def get_events(self):
        return pg.event.get()
