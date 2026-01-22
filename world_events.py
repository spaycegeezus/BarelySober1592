# world_events.py
import random
from math import sqrt
from database import instant_loss_locations, secret_locations, items

class WorldEventManager:
    def __init__(self, on_game_over=None, on_excursion=None, on_item_found=None):
        """
        Hooks:
          on_game_over(description)
          on_excursion(name, description)
          on_item_found(item)
        """
        self.on_game_over = on_game_over
        self.on_excursion = on_excursion
        self.on_item_found = on_item_found

        self.triggered_events = set()  # prevent repeat triggers

    def distance(self, lat1, lon1, lat2, lon2):
        return sqrt((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2)

    def pick_random_item(self, items_list):
        """Return a random item from a list for treasure events."""
        return random.choice(items_list)

    def check_events(self, lat, lon):
        # Check instant loss first
        for name, data in instant_loss_locations.items():
            if name in self.triggered_events:
                continue
            if self.distance(lat, lon, data["lat"], data["lon"]) < 0.5:
                self.triggered_events.add(name)
                if self.on_game_over:
                    self.on_game_over(data["description"])
                return "game_over"

        # Check secret excursions
        for name, data in secret_locations.items():
            if name in self.triggered_events:
                continue
            if self.distance(lat, lon, data["lat"], data["lon"]) < 0.5:
                self.triggered_events.add(name)
                if self.on_excursion:
                    self.on_excursion(name, data["description"])
                return "excursion"

        # Random treasure find chance (10% per check)
        if random.random() < 0.10:
            item = self.pick_random_item(items)
            if self.on_item_found:
                self.on_item_found(item)
            return "item_found"

        return None
