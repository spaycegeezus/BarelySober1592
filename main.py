# main.py
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
import matplotlib.pyplot as plt
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.graphics import PushMatrix, PopMatrix, Rotate
import database
from logic import Player
import random
import math
import time
import os
from minigames import CanonBlastMiniGame, PodiumMiniGame, CanonLoaderMiniGame, SeaBattleMiniGame, SabotageMiniGame, PearlDiverMiniGame, DiceRollingMiniGame
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.progressbar import ProgressBar
import sqlite3
import colorsys
from kivy.animation import Animation
from datetime import datetime, timedelta
from geopy.geocoders import Nominatim
from database import get_all_items, get_item_db_connection, init_databases
from database import get_all_ships, get_all_enemy_ships, get_ship_db_connection, enemy_vessels_data
from database import excursions, items, instant_loss_locations, secret_locations, populate_items, populate_ships, ships
from assets_loader import preload_assets, ASSET_FILES
from world_events import WorldEventManager
import json
from kivy.graphics import Color, Line, Rectangle, RoundedRectangle
from kivy.animation import Animation

SAVE_DIR = "game_data/saves"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

SAVE_DIR = "game_data/saves"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)


def save_game_to_slot(slot_index, player, current_location):
    """Save player and game metadata to the given slot."""
    path = os.path.join(SAVE_DIR, f"slot{slot_index}.json")

    # Build player dictionary (fully serializable)
    player_data = {
        "gold": player.gold,
        "dehydration_awareness": player.dehydration_awareness,
        "emergency_hydration": player.emergency_hydration,
        "combat_power": player.combat_power,
        "heading": player.heading,
        "speed": player._speed,
        "current_speed": player._current_speed,
        "capacity": player.capacity,
        "sails": player.sails,
        "fleet": player.fleet,
        "current_ship": player.current_ship,
        "navigation_items": player.navigation_items,
        "ship_capacity": player.ship_capacity,
        "durability_max": player.durability_max,
        "durability_current": player.durability_current,
        "portfolio": {k: list(v) for k, v in player.portfolio.items()},
        "game_time": player.game_time.isoformat(),
    }

    game_state = {
        "player": player_data,
        "location": current_location,
    }

    with open(path, "w") as f:
        json.dump(game_state, f, indent=2)


def load_game_from_slot(slot_index):
    """Load and return game_state dict from slot, or None."""
    path = os.path.join(SAVE_DIR, f"slot{slot_index}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        return json.load(f)


def get_save_slot_info():
    """Return readable info for each slot (timestamp + gold)."""
    slots = {}
    for i in range(1, 4):
        state = load_game_from_slot(i)
        if state and "player" in state:
            p = state["player"]
            time = datetime.fromisoformat(p["game_time"]).strftime("%b %d, %Y %I:%M %p")
            gold = p.get("gold", 0)
            slots[f"Slot {i}"] = f"{time} | gold: ${gold:,.2f}"
        else:
            slots[f"Slot {i}"] = "Empty"
    return slots


# --- Constants & Colors ---
WIDTH, HEIGHT = 800, 600
WHITE, BLACK, GREEN, RED, YELLOW = (255,255,255), (0,0,0), (0,255,0), (255,0,0), (255,255,0)

# --- Database ---

get_item_db_connection()
get_ship_db_connection()
init_databases()

# --- Database Paths ---
ITEM_DB_PATH = os.path.join("game_data", "item_market.db")
SHIP_DB_PATH = os.path.join("game_data", "ship_market.db")

# Set window size (optional)
Window.size = (800, 600)
player = Player()
player.journalistic_awareness = 0
bg_path = os.path.join(os.path.dirname(__file__), "Assets", "ancient_map.png")
bg = Image(source=bg_path, allow_stretch=True, keep_ratio=False)

# Ocean regions with visual and environmental variation
OCEAN_REGIONS = [
    {
        "name": "Arctic Ocean",
        "lat_range": (70, 90),
        "image": "Assets/choppy_ocean.png",
    },
    {
        "name": "North Atlantic Ocean",
        "lat_range": (30, 70),
        "image": "Assets/rough_ocean.png",
    },
    {
        "name": "Equatorial Seas",
        "lat_range": (-10, 30),
        "image": "Assets/calm_ocean.png",
    },
    {
        "name": "South Pacific",
        "lat_range": (-50, -10),
        "image": "Assets/choppy_ocean.png",
    },
    {
        "name": "Antarctic Ocean",
        "lat_range": (-90, -50),
        "image": "Assets/rough_ocean.png",
    },
]

def init_db():
    try:
        print("Initializing database...")
        populate_items()
        populate_ships()
        print("✅ Database ready.")
    except Exception as e:
        print(f"Database initialization failed: {e}")
    preload_assets()
    conn = sqlite3.connect("game_data/item_market.db")
    c = conn.cursor()
    for item in items:
        c.execute("""
                    INSERT OR REPLACE INTO items (name, sector, price, effect_min, effect_max, png, description)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
            item['name'],
            item['sector'],
            item['price'],
            item['effect'][0],
            item['effect'][1],
            item['png'],
            item['description']
        ))
        conn.commit()
        conn.close()

class LayeredBar(BoxLayout):
    def __init__(self, label_text="Bar", max_value=100, current_value=100, bar_color=(0, 1, 0, 1), **kwargs):
        # Pop your own parameters first so Kivy doesn't see them
        self.label_text = label_text
        self.max_value = max_value
        self.current_value = current_value
        self.bar_color = bar_color

        # Safe defaults for Kivy layout
        kwargs.setdefault("orientation", "vertical")
        kwargs.setdefault("size_hint", (None, None))  # Changed to allow absolute sizing
        kwargs.setdefault("height", 15)  # Default total height (thin!)
        super().__init__(**kwargs)

        # Label - make it smaller
        self.label = Label(
            text=self.label_text,
            size_hint=(1, None),
            height=15,  # Reduced from 20 to 10
            font_size='15sp'  # Smaller font for thin bar
        )

        # Container for bars - make it thinner
        self.bar_container = Widget(
            size_hint=(1, None),
            height= 7  # Reduced from 20 to 5 (very thin!)
        )

        with self.bar_container.canvas:
            # Background: thick red bar (permanent)
            Color(0.4, 0, 0, 1)
            self.bg_rect = RoundedRectangle(pos=self.bar_container.pos, size=self.bar_container.size)

            # Foreground: dynamic durability fill
            Color(*self.bar_color)
            self.fg_rect = RoundedRectangle(
                pos=self.bar_container.pos,
                size=(self.bar_container.width * (self.current_value / self.max_value), self.bar_container.height)
            )

        self.bar_container.bind(pos=self.update_rect, size=self.update_rect)
        self.add_widget(self.label)
        self.add_widget(self.bar_container)

        # Bind our own size changes to update the bar
        self.bind(size=self._on_size_change, pos=self._on_size_change)

    def _on_size_change(self, *args):
        """Update when the main widget size changes."""
        self.update_rect()

    def update_rect(self, *args):
        self.bg_rect.pos = self.bar_container.pos
        self.bg_rect.size = self.bar_container.size
        self.update_foreground()

    def update_foreground(self):
        if self.max_value > 0:
            percent = max(0, min(1, self.current_value / self.max_value))
            self.fg_rect.pos = self.bar_container.pos
            self.fg_rect.size = (self.bar_container.width * percent, self.bar_container.height)

    def set_value(self, new_value):
        self.current_value = new_value
        self.update_foreground()

    def update_display(self):
        """Update the bar display - called from external code."""
        self.update_foreground()

def safe_motion_notify(self, x, y, guiEvent=None):
    pass  # ignore mouse motion events

def reset_global_game_state():
    global player, dehydration_awareness, gold_fund, emergency_hydration, game_time, items

    init_databases()
    populate_ships()

    conn = sqlite3.connect("game_data/item_market.db")
    cursor = conn.cursor()

    # Create a completely new player with ALL attributes reset
    player = Player()
    player.gold = 15000  # starting gold
    player.portfolio = {}
    player.portfolio_data = []
    player.items_dict = []
    player.awareness = 0  # Dehydration Awareness (0-100)
    player.dehydration_awareness = 0
    player.emergency_hydration = 100  # Hydration
    player.combat_power = 10  # base combat ability
    player.heading = 0  # directional heading EAST
    player._speed = 2  # base speed
    player._current_speed = 1
    player.capacity = 1
    # Ship-related
    player.fleet = []
    player.items_scroll = []
    player.current_ship = None
    player.sails = 2
    player.navigation_items = []
    player.ship_capacity = 1
    player.base_ship_speed = 4
    player.dehydration_penalty = 0
    player.durability_max = []  # Maximum durability
    player.durability_current = 100  # Current durability
    player.game_time = datetime(1592, 6, 6, 6, 0)  # starting game date

    # Reset item prices to initial values
    for i, item in enumerate(items):
        cursor.execute("SELECT price, effect_min, effect_max FROM items WHERE name = ?", (item['name'],))
        row = cursor.fetchone()
        if row:
            item['price'] = row[0]
            item['effect'] = (row[1], row[2])

    conn.close()
    # Update ALL screens with the new player state
    try:
        # Get all screens
        user_screen = sm.get_screen("user_status_screen")
        sea_screen = sm.get_screen("sea_screen")
        ship_market_screen = sm.get_screen("ship_market_screen")
        item_market_screen = sm.get_screen("item_market_screen")

        # Reset SEA screen specific variables
        if hasattr(sea_screen, 'latitude'):
            sea_screen.latitude = 0.0  # Reset to 0.00
        if hasattr(sea_screen, 'longitude'):
            sea_screen.longitude = 0.0  # Reset to 0.00
        if hasattr(sea_screen, 'boat_x'):
            sea_screen.boat_x = 100  # Reset boat position
        if hasattr(sea_screen, 'boat_y'):
            sea_screen.boat_y = 50
        if hasattr(sea_screen, 'heading'):
            sea_screen.heading = 0

        # Clear SEA screen visual elements
        if hasattr(sea_screen, 'shadows'):
            for shadow in sea_screen.shadows[:]:
                sea_screen.remove_shadow(shadow)
            sea_screen.shadows = []

        # Reset ocean background
        if hasattr(sea_screen, 'ocean_canvas'):
            sea_screen.ocean_canvas.source = "Assets/calm_ocean.png"

        # Force refresh ALL screens
        user_screen.stats_label.text = user_screen.get_stats_text()
        if hasattr(user_screen, 'update_items_display'):
            user_screen.update_items_display()
        if hasattr(user_screen, 'update_time_display'):
            user_screen.update_time_display()
        if hasattr(user_screen, 'update_durability_display'):
            user_screen.update_durability_display()

        # Refresh ship market display
        if hasattr(ship_market_screen, 'fleet_label'):
            ship_market_screen.fleet_label.text = ship_market_screen.get_fleet_info()
        if hasattr(ship_market_screen, 'populate_ships'):
            ship_market_screen.populate_ships()

        # Refresh item market display
        if hasattr(item_market_screen, 'update_market_display'):
            item_market_screen.update_market_display()

        # Navigate to user status screen
        sm.current = "user_status_screen"

        print("DEBUG: Game state completely reset - fresh start!")

    except Exception as e:
        print(f"DEBUG: Error updating screens: {e}")
        # If screens don't exist yet, navigate to main menu
        sm.current = "main_menu"

    return player

class GhostButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (1, 0, 0, 0)  # fully transparent red base
        self.color = (1, 1, 1, 0.8)  # slightly visible white text
        self.bold = True

        with self.canvas.after:
            Color(1, 0, 0, 0.6)  # semi-transparent red border
            self.border_line = Line(rectangle=(self.x, self.y, self.width, self.height), width=1.5)

        self.bind(pos=self._update_border, size=self._update_border)

        # Hover tracking
        Window.bind(mouse_pos=self.on_mouse_pos)
        self.hovered = False

    def _update_border(self, *args):
        self.border_line.rectangle = (self.x, self.y, self.width, self.height)

    def on_mouse_pos(self, window, pos):
        if not self.get_root_window():
            return  # not yet added to screen
        inside = self.collide_point(*self.to_widget(*pos))
        if inside and not self.hovered:
            self.hovered = True
            self.reveal_effect()
        elif not inside and self.hovered:
            self.hovered = False
            self.hide_effect()

    def reveal_effect(self):
        # Fade in red background
        Animation(background_color=(1, 0, 0, 1), duration=0.3).start(self)

    def hide_effect(self):
        # Fade out to transparent again
        Animation(background_color=(1, 0, 0, 0), duration=0.5).start(self)

# Screens
class MainMenu(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        global game_time, ASSET_FILES
        # FloatLayout to layer background + widgets
        layout = FloatLayout()
        ASSET_FILES = preload_assets()

        # Background image
        bg = Image(source="Assets/ancient_map.png", allow_stretch=True, keep_ratio=False)
        layout.add_widget(bg)

        title_texture = ASSET_FILES["title"]["barely"]

        title = Image(
            texture=title_texture,
            size_hint=(None, None),
            size=(670, 270),
            pos_hint={'center_x': 0.5, 'top': 0.77},
            allow_stretch=True,
            keep_ratio=False
        )
        layout.add_widget(title)

        # UI buttons in a BoxLayout below title
        ui_layout = BoxLayout(
            orientation='horizontal',
            spacing=15,
            size_hint=(0.6, None),
            height=100,
            pos_hint={'center_x': 0.40, 'top': 0.45}
        )

        start_btn = GhostButton(text="Start Game", size_hint=(None, None), width=200, height=50)
        start_btn.bind(on_press=self.start_game)
        ui_layout.add_widget(start_btn)

        load_btn = GhostButton(text="Load Game", size_hint=(None, None), width=200, height=50)
        load_btn.bind(on_press=lambda x: self.show_load_popup())
        ui_layout.add_widget(load_btn)

        mini_game_btn = GhostButton(text="Mini Games", size_hint=(None, None), width=200, height=50)
        mini_game_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'game_menu'))
        ui_layout.add_widget(mini_game_btn)

        layout.add_widget(ui_layout)
        self.add_widget(layout)

    def on_enter(self, *args):
        entry = App.get_running_app().entry_path
        print(f"DEBUG: MainMenu.on_enter() - entry_path = {entry}")

        if entry == "start":
            print("DEBUG: Resetting game state for new game")
            reset_global_game_state()
            # Clear the flag after use
            App.get_running_app().entry_path = None
        elif entry == "load":
            print("DEBUG: Loaded game state, skipping reset")
            # Clear the flag after use
            App.get_running_app().entry_path = None
        elif entry == "mini":
            print("DEBUG: Player entered from mini-game pathway")
            # Don't clear this one as it might be used elsewhere
        else:
            print("DEBUG: No entry path set - normal menu navigation")

    def show_load_popup(self):
        slots = get_save_slot_info()
        layout = BoxLayout(orientation="vertical", spacing=10, padding=10)

        for i, slot_name in enumerate(slots.keys(), 1):
            btn = Button(text=f"{slot_name} - {slots[slot_name]}", size_hint_y=None, height=40)
            btn.bind(on_press=lambda instance, idx=i: self.load_from_slot(idx))
            layout.add_widget(btn)

        popup = Popup(title="Load Game", content=layout, size_hint=(0.7, 0.5))
        popup.open()

    def restart_game(self):
        """Restart the game completely"""
        self.start_game()

    def start_game(self, instance=None):
        """Start a new game - COMPLETED METHOD"""
        print("DEBUG: Starting new game...")

        # Set entry path to trigger reset in on_enter
        App.get_running_app().entry_path = "start"

        # Reset game state
        reset_global_game_state()

        # Navigate to user status screen
        self.manager.current = "user_status_screen"

        print("DEBUG: New game started successfully!")

    def go_to_mini_games(self, instance):
        App.get_running_app().entry_path = "mini"
        print(f"DEBUG: Mini game pathway set")
        self.manager.current = "game_menu"

    def load_from_slot(self, slot_index):
        state = load_game_from_slot(slot_index)
        if not state:
            Popup(
                title="Empty Slot",
                content=Label(text="No save in this slot."),
                size_hint=(0.5, 0.3)
            ).open()
            return

        p = state["player"]
        player = self.manager.get_screen("user_status_screen").player

        # Restore all values
        player.gold = p.get("gold", 0)
        player.dehydration_awareness = p.get("dehydration_awareness", 0)
        player.emergency_hydration = p.get("emergency_hydration", 100)
        player.combat_power = p.get("combat_power", 10)
        player.heading = p.get("heading", 0)
        player._speed = p.get("speed", 1)
        player._current_speed = p.get("current_speed", 1)
        player.capacity = p.get("capacity", 1)
        player.sails = p.get("sails", 2)
        player.fleet = p.get("fleet", [])
        player.current_ship = p.get("current_ship")
        player.navigation_items = p.get("navigation_items", [])
        player.ship_capacity = p.get("ship_capacity", 1)
        player.durability_max = p.get("durability_max", 100)
        player.durability_current = p.get("durability_current", 100)
        player.portfolio = {k: tuple(v) for k, v in p.get("portfolio", {}).items()}
        player.game_time = datetime.fromisoformat(p["game_time"])

        self.manager.current = state["location"]

        # Refresh UI
        screen = self.manager.get_screen(state["location"])
        if hasattr(screen, "update_items_display"):
            screen.update_items_display()
        if hasattr(screen, "update_time_display"):
            screen.update_time_display()

class UserStatusScreen(Screen):
    def __init__(self, player, game_over_screen=None, **kwargs):
        super().__init__(**kwargs)
        global ASSET_FILES
        self.player = player
        self.game_over_screen = game_over_screen
        self.portfolio = []
        self.player.durability_current = (sum(ship.get("durability_current", 100) for ship in self.player.fleet) / len(self.player.fleet) if self.player.fleet else 100)
        self.player.durability_max = (sum(ship.get("durability_max", 100) for ship in self.player.fleet) / len(self.player.fleet) if self.player.fleet else 100)
        self.layout = FloatLayout()

        layout = FloatLayout()
        ASSET_FILES = preload_assets()

        # Background image
        bg = Image(source="Assets/captain_quarters.png", allow_stretch=True, keep_ratio=False)
        self.layout.add_widget(bg)

        title_main = ASSET_FILES["title"]["captainquartertitle"]
        subtitle_main = ASSET_FILES["title"]["vessel"]

        title = Image(
            texture=title_main,
            size_hint=(None, None),
            size=(400, 100),
            pos_hint={'center_x': 0.35, 'top': 0.95},
            allow_stretch=True,
            keep_ratio=False
        )
        with title.canvas.before:
            PushMatrix()
            self.title_rot = Rotate(angle=10, origin=title.center)  # tilt up toward right
        with title.canvas.after:
            PopMatrix()

        self.layout.add_widget(title)

        # Subtitle
        subtitle = Image(
            texture=subtitle_main,
            size_hint=(None, None),
            size=(200, 90),
            pos_hint={'center_x': 0.82, 'top': .99},
            allow_stretch=True,
            keep_ratio=False
        )

        self.layout.add_widget(subtitle)

        # Time label
        self.time_label = Label(
            text=self.player.game_time.strftime('%B %d, %Y - %I:%M %p'),
            font_size=20,
            bold=True,
            size_hint=(None, None),
            size=(400, 40),
            pos_hint={'center_x': 0.82, 'top': 0.85}
        )
        self.layout.add_widget(self.time_label)

        # Player and fleet stats as two labels
        self.player_stats_label = Label(
            text=self.get_player_stats_text(),
            font_size=17,
            bold=True,
            size_hint=(None, None),
            markup=True,
            size=(350, 150),
            halign="left",
            valign="top",
            pos_hint={'x': 0.0, 'top': 0.80}
        )
        self.player_stats_label.bind(size=self.player_stats_label.setter('text_size'))
        self.layout.add_widget(self.player_stats_label)

        self.fleet_stats_label = Label(
            text=self.get_fleet_stats_text(),
            font_size=17,
            bold=True,
            size_hint=(None, None),
            markup=True,
            size=(350, 150),
            halign="left",
            valign="top",
            pos_hint={'right': 0.95, 'top': 0.80}
        )
        self.fleet_stats_label.bind(size=self.fleet_stats_label.setter('text_size'))
        self.layout.add_widget(self.fleet_stats_label)

        # items scroll
        self.items_scroll = ScrollView(size_hint=(0.8, 0.20), pos_hint={'x': 0.05, 'y': 0.35})
        self.items_grid = GridLayout(cols=2, size_hint_y=None, spacing=10)
        self.items_grid.bind(minimum_height=self.items_grid.setter('height'))
        self.items_scroll.add_widget(self.items_grid)
        self.layout.add_widget(self.items_scroll)
        # Outer vertical layout
        btn_layout = BoxLayout(
            orientation="vertical",
            size_hint=(0.9, None),
            opacity=0.6,
            height=70,
            spacing=10,
            pos_hint={'x': 0.05, 'y': 0.05}
        )
        if getattr(self.player, "fleet", None) and len(self.player.fleet) > 0:
            self.player.durability_current = sum(
                ship.get("durability_current", 100) for ship in self.player.fleet) / len(self.player.fleet)
            self.player.durability_max = sum(ship.get("durability_max", 100) for ship in self.player.fleet) / len(
                self.player.fleet)
        else:
            # Default values when no ships exist yet
            self.player.durability_current = 100
            self.player.durability_max = 100

        # Row 1: gameplay flow buttons
        row1 = BoxLayout(size_hint_y=None, height=40, spacing=10)
        for text, method in [
            ("Go on a excursion", self.go_to_excursion),
            ("Harbor and Market", self.go_to_items),
            ("Shipyard Repair", self.repair_ship),
        ]:
            btn = Button(text=text)
            btn.bind(on_press=method)
            row1.add_widget(btn)

        # Row 2: gameplay flow buttons
        row2 = BoxLayout(size_hint_y=None, height=40, spacing=10)
        for text, method in [
            ("Shipwright & Dockyard", self.go_to_ships),
            ("Travel via SEA", self.go_to_SEA),
            ("Use hydration ", self.emergency_hydration_intervention),
        ]:
            btn = Button(text=text)
            btn.bind(on_press=method)
            row2.add_widget(btn)

        # Row 2: utility buttons
        row3 = BoxLayout(size_hint_y=None, height=40, spacing=10)
        for text, method in [
            ("Save Game", lambda instance: self.show_save_popup()),
            ("Exit to Main Menu", self.confirm_exit),
        ]:
            btn = Button(text=text)
            btn.bind(on_press=method)
            row3.add_widget(btn)

        btn_layout.add_widget(row1)
        btn_layout.add_widget(row2)
        btn_layout.add_widget(row3)
        self.layout.add_widget(btn_layout)
        self.add_widget(self.layout)

    def repair_ship(self, instance=None):
        print("repair_ship triggered!")
        """Repair all ships in the fleet with confirmation."""
        if not self.player.fleet:
            Popup(title="No Ships",
                  content=Label(text="You don't have any ships to repair!"),
                  size_hint=(0.5, 0.3)).open()
            return

        # Calculate cost properly
        repair_cost = (self.player.durability_max - self.player.durability_current) * 1.1

        if repair_cost <= 0:
            Popup(title="No Repairs Needed",
                  content=Label(text="Your fleet is already at full durability!"),
                  size_hint=(0.5, 0.3)).open()
            return

        # Create confirmation popup
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        current_percent = self.player.get_fleet_durability_percentage()

        message = (f"Repair fleet to 100%?\n\n"
                   f"Current: {current_percent:1.1f}%\n"
                   f"Cost: ${repair_cost:,.2f}\n"
                   f"Your gold: ${self.player.gold:,.2f}")

        content.add_widget(Label(text=message, halign='center'))
        self.update_durability_display()

        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        confirm_btn = Button(text="Repair", background_color=(0.2, 0.8, 0.2, 1))
        cancel_btn = Button(text="Cancel", background_color=(0.8, 0.2, 0.2, 1))
        btn_layout.add_widget(confirm_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)

        popup = Popup(title="Shipyard Repair", content=content, size_hint=(0.6, 0.5))

        def do_repair(instance):
            try:
                if self.player.gold >= repair_cost:
                    self.player.gold -= repair_cost
                    self.player.repair_all_ships()
                    if hasattr(self, "update_ui_after_repair"):
                        self.update_ui_after_repair()
                        self.update_durability_display()
                    popup.dismiss()
                    Popup(title="Repair Complete",
                          content=Label(text="Fleet restored to 100% durability!"),
                          size_hint=(0.5, 0.3)).open()
                else:
                    popup.dismiss()
                    needed = repair_cost - self.player.gold
                    Popup(title="Insufficient Gold",
                          content=Label(text=f"Need ${needed:,.2f} more!"),
                          size_hint=(0.5, 0.3)).open()
            except Exception as e:
                popup.dismiss()
                Popup(title="Repair Error",
                      content=Label(text=f"An error occurred: {e}"),
                      size_hint=(0.6, 0.4)).open()
                raise

        confirm_btn.bind(on_press=do_repair)
        cancel_btn.bind(on_press=popup.dismiss)
        popup.open()

    def show_save_popup(self, post_save_callback=None):
        slots = get_save_slot_info()
        layout = BoxLayout(orientation="vertical", spacing=10, padding=10)

        for i, slot_name in enumerate(slots.keys(), 1):
            btn = Button(text=f"{slot_name} - {slots[slot_name]}", size_hint_y=None, height=40)
            btn.bind(on_press=lambda instance, idx=i: self.save_to_slot(idx, instance, post_save_callback))
            layout.add_widget(btn)

        popup = Popup(title="Choose Save Slot", content=layout, size_hint=(0.7, 0.5))
        self.save_popup = popup
        popup.open()

    def confirm_exit(self, instance):
        layout = BoxLayout(orientation="vertical", spacing=10, padding=10)

        label = Label(
            text="Are you sure you want to exit to the Main Menu?\n\nUnsaved progress will be lost!",
            halign="center"
        )
        layout.add_widget(label)

        # button row
        btn_row = BoxLayout(size_hint_y=None, height=50, spacing=10)

        save_btn = Button(text="Save & Exit")
        dont_save_btn = Button(text="Exit Without Saving")
        cancel_btn = Button(text="Cancel")

        btn_row.add_widget(save_btn)
        btn_row.add_widget(dont_save_btn)
        btn_row.add_widget(cancel_btn)

        layout.add_widget(btn_row)

        popup = Popup(title="Confirm Exit", content=layout, size_hint=(0.7, 0.5))

        # Bind button actions
        def do_save_exit(*args):
            popup.dismiss()
            # Open the normal save popup but pass a post-save action
            def exit_after_save():
                self.exit_to_main_menu()
            self.show_save_popup(post_save_callback=exit_after_save)

        def do_exit(*args):
            global player
            popup.dismiss()
            self.exit_to_main_menu()

        def do_cancel(*args):
            popup.dismiss()

        save_btn.bind(on_press=do_save_exit)
        dont_save_btn.bind(on_press=do_exit)
        cancel_btn.bind(on_press=do_cancel)

        popup.open()

    def save_to_slot(self, slot_index, button_instance=None, post_save_callback=None):
        save_game_to_slot(slot_index, self.player, self.manager.current)

        if hasattr(self, "save_popup"):
            self.save_popup.dismiss()

        Popup(
            title="Saved",
            content=Label(text=f"Game saved to Slot {slot_index}"),
            size_hint=(0.5, 0.3)
        ).open()

        if post_save_callback:
            post_save_callback()

    def update_ui_after_repair(self):
        """Update all UI elements after repair."""
        self.update_durability_stats()
        self.stats_label.text = self.get_stats_text()

        # If you have a gold display, update it too
        if hasattr(self, 'gold_label'):
            self.gold_label.text = f"Gold: ${self.player.gold:,.2f}"

    def update_durability_stats(self):
        if getattr(self.player, "fleet", None) and len(self.player.fleet) > 0:
            self.player.durability_current = sum(
                ship.get("durability_current", 100) for ship in self.player.fleet) / len(self.player.fleet)
            self.player.durability_max = sum(ship.get("durability_max", 100) for ship in self.player.fleet) / len(
                self.player.fleet)
        else:
            self.player.durability_current = 100
            self.player.durability_max = 100
        self.durability_bar.max = self.player.durability_max
        self.durability_bar.value = self.player.durability_current

    def set_player(self, player):
        self.player = player

    def advance_time(self, hours=1):
        """Advance game time and update items when user acts"""
        self.player.game_time += timedelta(hours=hours)

        # Update item prices whenever time advances
        self.player.update_item_prices(items)

        self.update_time_display()
        self.update_items_display()

    def get_player_stats_text(self):
        """Left column — Player stats"""

        def col(left, right, width=15):
            return f"[b]{left:<{width}}[/b] {right}"

        stats = [
            col("Gold:", f"${self.player.gold:,.2f}"),
            col("Hydration:", f"{self.player.emergency_hydration:.0f}/100"),
            col("Dehydration:", f"{self.player.dehydration_awareness:.0f}/100"),
            col("Combat Power:", f"{self.player.combat_power:.1f}")
        ]
        return "\n".join(stats)

    def get_fleet_stats_text(self):
        """Right column — Fleet stats"""

        def col(left, right, width=15):
            return f"[b]{left:<{width}}[/b] {right}"

        if self.player.fleet:
            ship_count = len(self.player.fleet)
            total_base_speed = sum(ship.get('base_speed', 1) for ship in self.player.fleet)
            total_capacity = sum(ship.get('capacity', 0) for ship in self.player.fleet)
            avg_durability = sum(ship.get('durability_current', 1) for ship in self.player.fleet) / ship_count
            nav_count = len(getattr(self.player, 'navigation_items', []))

            info = [
                col("Fleet:  ", f"{ship_count} ships"),
                col("Fleet Durability:  ", f"{avg_durability:.2f}%"),
                col("Base Fleet Speed:  ", f"{total_base_speed:.1f} knots"),
                col("Total Fleet Capacity:  ", f"{self.player.capacity:.0f} (Base: {total_capacity})"),
                col("Navigation:", str(nav_count)),
            ]
            if ship_count <= 2:
                names = ", ".join(ship['name'] for ship in self.player.fleet)
                info.append(col("Ships:", names))
        else:
            info = [col("Fleet:", "No ships")]
        return "\n".join(info)

    def update_items_display(self):
        """Refresh the items scroll view"""
        self.items_grid.clear_widgets()

        if self.player.portfolio:
            # Build a dict for fast price lookup
            items_dict = {s['name']: s for s in items}

            for name, value in self.player.portfolio.items():
                try:
                    # Normalize saved data
                    if isinstance(value, tuple) and len(value) == 2:
                        units, total_cost = value
                        units = int(units)
                        total_cost = float(total_cost)
                        avg_price = total_cost / units if units > 0 else 0
                    else:
                        # If legacy/int-only save format
                        units = int(value)
                        avg_price = items_dict.get(name, {'price': 0})['price']

                    # Always float current_price
                    current_price = float(items_dict.get(name, {'price': avg_price})['price'])
                    print(f"DEBUG: {name} current_price = {current_price}")

                    # Look up item data
                    item_data = items_dict.get(name, {})

                    # Generate effect description
                    if 'effect' in item_data:
                        min_eff, max_eff = item_data['effect']
                        sector = item_data.get('sector', 'General')

                        # Text describing the impact
                        if sector == "Ship":
                            effect_text = f"Speed +{min_eff:.1f} to +{max_eff:.1f}"
                        elif sector == "Drink":
                            effect_text = f"Hydration +{abs(min_eff):.1f} to +{abs(max_eff):.1f}"
                        elif sector == "Combat":
                            effect_text = f"Combat +{min_eff:.1f} to +{max_eff:.1f}"
                        elif sector == "Cargo":
                            effect_text = f"Capacity +{min_eff:.1f} to +{max_eff:.1f}"
                        elif sector == "Drift":
                            effect_text = f"Drift -{abs(min_eff):.1f} to -{abs(max_eff):.1f}"
                        else:
                            effect_text = f"Effect: {min_eff:.1f} to {max_eff:.1f}"
                    else:
                        effect_text = "No effect data."

                    purchase_label = Label(
                        text=f"{name} x{units}\n{effect_text}",
                        size_hint_y=None, height=50, halign="left"
                    )

                    purchase_label.bind(size=purchase_label.setter('text_size'))
                    purchase_label.text_size = (purchase_label.width, None)

                    # Current market value
                    current_label = Label(
                        text=f"${current_price:.2f} each = ${current_price * units:.2f}",
                        size_hint_y=None, height=30, halign="right"
                    )
                    current_label.bind(size=current_label.setter('text_size'))
                    current_label.text_size = (current_label.width, None)

                    # Debug portfolio vs item lookup
                    print(f"Portfolio: {name}, lookup in items: {[s['name'] for s in items]}")

                    # Force texture update so labels resize correctly
                    purchase_label.texture_update()
                    current_label.texture_update()

                    self.items_grid.add_widget(purchase_label)
                    self.items_grid.add_widget(current_label)

                except Exception as e:
                    # Graceful fallback
                    error_label = Label(
                        text=f"{name}: Error loading item ({e})",
                        size_hint_y=None, height=30
                    )
                    self.items_grid.add_widget(error_label)
                    self.items_grid.add_widget(Label(text="", size_hint_y=None, height=30))

        else:
            self.items_grid.add_widget(Label(text="No items owned", size_hint_y=None, height=30))
            self.items_grid.add_widget(Label(text="", size_hint_y=None, height=30))

    def update_time(self, dt):
        # Update existing label instead of creating a new one
        self.time_label.text = self.player.game_time.strftime('%B %d, %Y - %I:%M %p')

        # Centralized check for game over
        if self.player.dehydration_awareness >= 100 and self.manager.current != "game_over":
            go_screen = self.manager.get_screen("game_over")
            go_screen.finalize(
                self.player,
                reason="You have been exposed! Your propaganda network has collapsed."
            )

            self.manager.current = "game_over"

    def update_time_display(self, dt=None):
        """Update the clock and stats labels without touching items."""
        self.time_label.text = self.player.game_time.strftime('%B %d, %Y - %I:%M %p')
        self.player_stats_label.text = self.get_player_stats_text()
        self.fleet_stats_label.text = self.get_fleet_stats_text()

    def emergency_hydration_intervention(self, instance):
        # First, check if player has any Drink items in portfolio
        drink_items_owned = False
        drink_item_name = None

        for item_name, (units, cost) in self.player.portfolio.items():
            # Check if this is a Drink sector item and player owns at least 1
            for item_data in items:  # Assuming 'items' is imported from database
                if item_data["name"] == item_name and item_data["sector"] == "Food/Drink" and units > 0:
                    drink_items_owned = True
                    drink_item_name = item_name
                    break
            if drink_items_owned:
                break

        message = ""

        # Option 1: Player has Drink items to use
        if drink_items_owned and self.player.emergency_hydration > 0:
            # Use one drink item from portfolio
            current_units, total_cost = self.player.portfolio[drink_item_name]
            self.player.portfolio[drink_item_name] = (current_units - 1, total_cost)

            # Remove if no units left
            if current_units - 1 <= 0:
                del self.player.portfolio[drink_item_name]

            # Get the drink effect
            drink_effect = 0
            for item_data in items:
                if item_data["name"] == drink_item_name:
                    drink_effect += random.uniform(item_data["effect"][0], item_data["effect"][1])
                    break

            # Apply effects
            self.player.dehydration_awareness = max(0, self.player.dehydration_awareness - abs(drink_effect))
            self.player.emergency_hydration -= 1

            message = f"You used {drink_item_name}. Dehydration reduced by {10 + abs(drink_effect):.2f}%. Remaining: {self.player.emergency_hydration}"

        # Option 2: Player has gold to pay the "GODS of the SEA"
        elif self.player.emergency_hydration > 0:
            cost = 20000 if self.player.dehydration_awareness > 50 else 1000

            if self.player.gold >= cost:
                self.player.gold -= cost
                self.player.dehydration_awareness = 0
                self.player.emergency_hydration -= 1
                message = f"You paid the GODS of the SEA with gold. Dehydration reset to 0! Cost: ${cost}"
            else:
                message = f"Insufficient gold! Need ${cost}, but only have ${self.player.gold:.2f}"

        # Option 3: No hydration meter remaining
        else:
            message = "No hydration remaining! You're completely dehydrated!"

        # Create the popup
        popup = Popup(
            title="Hydration Intervention",
            content=Label(text=message),
            size_hint=(0.7, 0.4)
        )

        # Bind an on_dismiss callback to update the screen after popup closes
        def refresh_screen(*args):
            self.update_items_display()
            self.update_time_display()
            self.stats_label.text = self.get_stats_text()

        popup.bind(on_dismiss=refresh_screen)
        popup.open()

    def go_to_ships(self, instance):
        self.advance_time(hours=1)
        populate_ships()
        self.manager.current = "ship_market"

    def go_to_excursion(self, instance):
        self.advance_time(hours=1)
        self.manager.current = "excursion_select"

    def go_to_items(self, instance):
        self.advance_time(hours=1)
        self.manager.current = "item_market"

    def go_to_SEA(self, instance):
        """Check if player has ships before going to SEA screen."""
        if not getattr(self.player, "fleet", None) or len(self.player.fleet) == 0:
            Popup(
                title="No Vessels!",
                content=Label(text="You need at least one ship to sail!\nVisit the Shipwright & Dockyard first."),
                size_hint=(0.6, 0.4)
            ).open()
            return

        self.advance_time(hours=1)  # Time to prepare for voyage
        self.manager.current = "SEA_screen"

    def exit_to_main_menu(self):
        self.manager.current = "main_menu"

class ShipMarketScreen(Screen):
    def __init__(self, player, **kwargs):
        super().__init__(**kwargs)
        self.player = player
        self.layout = FloatLayout()

        # --- Background ---
        bg = Image(source="Assets/ship_market.png", allow_stretch=True, keep_ratio=False)
        self.layout.add_widget(bg)

        # --- Title ---
        title = Label(
            text="Shipwright & Dockyard",
            font_size=40,
            size_hint=(None, None),
            pos_hint={'center_x': 0.5, 'top': 0.95}
        )
        self.layout.add_widget(title)

        # --- Fleet info ---
        self.fleet_label = Label(
            text=self.get_fleet_info(),
            font_size=16,
            size_hint=(0.9, None),
            height=100,
            halign='center',
            valign='center',
            pos_hint={'x': 0.05, 'top': 0.87}
        )
        self.layout.add_widget(self.fleet_label)

        # --- ScrollView & Grid ---
        self.scroll = ScrollView(
            size_hint=(0.8, 0.4),
            pos_hint={'center_x': 0.5, 'y': 0.2},
            bar_color=(0.2, 0.25, 0.25, 0.7),
            bar_inactive_color=(0.6, 0.5, 0.4, 0.3),
            do_scroll_x=False
        )

        # Create grid for ships
        self.grid = GridLayout(
            cols=1,
            spacing=10,
            padding=10,
            size_hint_y=None
        )
        self.grid.bind(minimum_height=self.grid.setter('height'))

        # Attach grid inside scroll
        self.scroll.add_widget(self.grid)

        # Add scroll to layout (so the grid shows inside)
        self.layout.add_widget(self.scroll)

        # --- Back button ---
        back_btn = Button(
            text="Return to Captain's Quarter",
            size_hint=(None, None),
            width=220,
            height=60,
            background_normal='',
            background_color=(0.58, 0.58, 0.58, 1),
            color=(0.15, 0.18, 0.1, 1),
            bold=True,
            pos_hint={'center_x': 0.5, 'y': 0.05}
        )
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'user_status_screen'))
        self.layout.add_widget(back_btn)

        # --- Final setup ---
        self.add_widget(self.layout)

        # Populate ships once everything exists
        populate_ships()

    def on_pre_enter(self):
        """Called when screen is about to be shown"""
        # Refresh fleet info every time we enter the screen
        self.fleet_label.text = self.get_fleet_info()
        self.populate_market_ships()

    def get_fleet_info(self):
        """Get current fleet information."""
        # Safely check if fleet exists and is a list
        if not hasattr(self.player, 'fleet') or not self.player.fleet:
            return "No ships in fleet\nStart by purchasing your first ship!"

        ship_count = len(self.player.fleet)
        total_base_speed = sum(ship.get('base_speed', 1) for ship in self.player.fleet)
        total_capacity = sum(ship.get('capacity', 0) for ship in self.player.fleet)

        # Get final speed with multipliers
        final_speed = self.player.speed if hasattr(self.player, 'speed') else total_base_speed

        return f"Fleet: {ship_count} ships\nFinal Speed: {final_speed:.1f} (Base: {total_base_speed})\nCapacity: {total_capacity}"

    def refresh_user_status_screen(self):
        """Refresh the user status screen to show updated fleet"""
        try:
            if hasattr(self.manager, "get_screen"):
                status_screen = self.manager.get_screen("user_status_screen")
                # Update the durability bars and stats
                if hasattr(status_screen, 'update_time_display'):
                    status_screen.update_time_display()
                if hasattr(status_screen, 'update_durability_bars'):
                    status_screen.update_durability_bars()
        except Exception as e:
            print(f"Error refreshing user status: {e}")

    def populate_market_ships(self):
        """Populate the ship market with available ships."""
        self.grid.clear_widgets()

        conn = sqlite3.connect("game_data/ship_market.db")
        c = conn.cursor()
        c.execute("SELECT name, price, base_speed, capacity, sails_multiplier, png FROM ships")
        ships_data = c.fetchall()
        conn.close()
        print(f"DEBUG: Retrieved {len(ships_data)} ships from database.")

        if not ships_data:
            print("⚠️ No ships found. Check if 'populate_ships()' ran and database path is correct.")

        for ship in ships_data:
            name, price, base_speed, capacity, sails_multiplier, png = ship
            info = f"{name} - ${price:,} | Speed: {base_speed} | Capacity: {capacity} | Sails:{sails_multiplier}"

            # Create a more detailed button layout
            btn_layout = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=70,
                spacing=10,
                padding=5
            )

            # Info label
            info_label = Label(
                text=info,
                size_hint_x=0.8,
                halign='left',
                valign='middle'
            )
            info_label.bind(size=info_label.setter('text_size'))

            # View button
            view_btn = Button(
                text="View Ship",
                size_hint_x=0.2,
                background_color=(0.3, 0.5, 0.7, 1),
                color=(1, 1, 1, 1)
            )
            view_btn.bind(on_press=lambda instance, n=name, p=price, bs=base_speed, cap=capacity, sail=sails_multiplier:
            self.show_ship_popup(n, p, bs, cap, sail))

            # Buy button
            buy_btn = Button(
                text="Buy",
                size_hint_x=0.2,
                background_color=(0.2, 0.7, 0.3, 1),
                color=(1, 1, 1, 1)
            )
            buy_btn.bind(on_press=lambda instance, n=name, p=price, bs=base_speed, cap=capacity, sail=sails_multiplier:
            self.buy_ship(n, p, bs, cap, sail))

            btn_layout.add_widget(info_label)
            btn_layout.add_widget(view_btn)
            btn_layout.add_widget(buy_btn)

            self.grid.add_widget(btn_layout)

    def get_ship_image_path(self, ship_name):
        """Map ship names to image files."""
        ship_images = {
        "rowboat": "rowboat.png",
        "fishing_skiff": "fishing_skiff.png",
        "dinghy": "dinghy.png",
        "cutter": "cutter.png",
        "sloop": "sloop.png",
        "schooner": "schooner.png",
        "merchant_schooner": "merchant_schooner.png",
        "cursed_dinghy": "cursed_dinghy.png",

        # ------------------------
        # Mid-Tier Ships
        # ------------------------
        "brigantine": "brigantine.png",
        "barque": "barque.png",
        "caravel": "caravel.png",
        "carrack": "carrack.png",
        "corvette": "corvette.png",
        "brig_o_war": "brig_o_war.png",
        "manowar": "manowar.png",
        "ghost_frigate": "ghost_frigate.png",
        "clipper_ship": "clipper_ship.png",

        # ------------------------
        # Large / Advanced Ships
        # ------------------------
        "galleon": "galleon_print.png",
        "royal_frigate": "royal_frigate.png",
        "dragon_ship": "dragon_ship.png",
        "sea_serpent": "sea_serpent_ship.png",
        "leviathan": "leviathan_ship_print.png",

        # ------------------------
        # Extreme / Legendary Ships
        # ------------------------
        "flying_dutchman": "flying_dutchman.png",
        "kraken_maw": "kraken_maw_ship.png",
        "phoenix_galleon": "phoenix_galleon_ship.png",
        "tempest_clipper": "tempest_clipper.png",
        "celestial_caravel": "celestial_caravel.png",
        "dread_leviathan": "dread_leviathan_ship.png",
        "aurora_frigate": "aurora_frigate.png",
        "stormbreaker": "stormbreaker_print.png",

        }

        # Try to find matching image
        for key, image_file in ship_images.items():
            if key in ship_name.lower():
                return f"Assets/{image_file}"

        # Default ship image
        return "Assets/boat.png"

    def show_ship_popup(self, name, price, base_speed, capacity, sails_multiplier):
        """Show a popup with ship details and image."""
        content = BoxLayout(
            orientation='vertical',
            spacing=10,
            padding=20,
            size_hint=(1, 1)
        )

        # Ship image
        ship_image_path = self.get_ship_image_path(name)
        try:
            ship_image = Image(
                source=ship_image_path,
                size_hint=(1, 0.6),
                allow_stretch=True,
                keep_ratio=True
            )
            content.add_widget(ship_image)
        except:
            # Fallback if image doesn't exist
            fallback_label = Label(
                text=f"[Image: {name}]",
                size_hint=(1, 0.3),
                font_size=20,
                bold=True
            )
            content.add_widget(fallback_label)

        # Ship details
        details_text = (
            f"[b]{name}[/b]\n\n"
            f"Price: ${price:,}\n"
            f"Base Speed: {base_speed}\n"
            f"Capacity: {capacity} units\n"
            f"Sails Multiplier: x{sails_multiplier}\n\n"
            f"Total Cost: ${price:,}"
        )

        details_label = Label(
            text=details_text,
            markup=True,
            size_hint=(1, 0.4),
            halign='center',
            valign='middle'
        )
        details_label.bind(size=details_label.setter('text_size'))
        content.add_widget(details_label)

        # Action buttons
        button_layout = BoxLayout(
            size_hint=(1, 0.2),
            spacing=10
        )

        buy_btn = Button(
            text=f"Buy for ${price:,}",
            background_color=(0.2, 0.7, 0.3, 1),
            color=(1, 1, 1, 1)
        )
        buy_btn.bind(
            on_press=lambda x: self.buy_ship_from_popup(name, price, base_speed, capacity, sails_multiplier, popup))

        close_btn = Button(
            text="Close",
            background_color=(0.7, 0.2, 0.2, 1),
            color=(1, 1, 1, 1)
        )

        button_layout.add_widget(buy_btn)
        button_layout.add_widget(close_btn)
        content.add_widget(button_layout)

        # Create and open popup
        popup = Popup(
            title="Ship Details",
            content=content,
            size_hint=(0.8, 0.8)
        )

        close_btn.bind(on_press=popup.dismiss)
        popup.open()

    def buy_ship_from_popup(self, name, price, base_speed, capacity, sails_multiplier, popup):
        """Handle ship purchase from the popup."""
        if self.player.gold >= price:
            # Create ship data
            ship_data = {
                'name': name,
                'price': price,
                'base_speed': base_speed,
                'capacity': capacity,
                'sails_multiplier': sails_multiplier
            }

            # Add to fleet
            self.player.gold -= price
            self.player.add_ship(ship_data)

            # Update display
            self.fleet_label.text = self.get_fleet_info()

            # Close the detail popup
            popup.dismiss()

            # Show success popup
            success_popup = Popup(
                title="Ship Added to Fleet!",
                content=Label(text=f"The {name} has joined your armada!\nTotal ships: {len(self.player.fleet)}"),
                size_hint=(0.6, 0.4)
            )
            success_popup.open()

            # Refresh UserStatusScreen
            if hasattr(self.manager, "get_screen"):
                try:
                    status_screen = self.manager.get_screen("user_status_screen")
                    status_screen.update_time_display()
                except Exception:
                    pass
        else:
            # Show error but keep the detail popup open
            error_popup = Popup(
                title="Not Enough Gold",
                content=Label(text=f"You need ${price - self.player.gold:,.2f} more!"),
                size_hint=(0.6, 0.4)
            )
            error_popup.open()

    def buy_ship(self, name, price, base_speed, capacity, sails_multiplier):
        """Purchase a ship directly (for the original buy buttons)."""
        if self.player.gold >= price:
            # Create ship data
            ship_data = {
                'name': name,
                'price': price,
                'base_speed': base_speed,
                'capacity': capacity,
                'sails_multiplier': sails_multiplier
            }

            # Add to fleet
            self.player.gold -= price
            self.player.add_ship(ship_data)

            # Update display
            self.fleet_label.text = self.get_fleet_info()

            popup = Popup(
                title="Ship Added to Fleet!",
                content=Label(text=f"The {name} has joined your armada!\nTotal ships: {len(self.player.fleet)}"),
                size_hint=(0.6, 0.4)
            )
            popup.open()

            # Refresh UserStatusScreen
            if hasattr(self.manager, "get_screen"):
                try:
                    status_screen = self.manager.get_screen("user_status_screen")
                    status_screen.update_time_display()
                except Exception:
                    pass
        else:
            Popup(
                title="Not Enough Gold",
                content=Label(text=f"You need ${price - self.player.gold:,.2f} more!"),
                size_hint=(0.6, 0.4)
            ).open()

class DataManager:
    """Centralized data management to eliminate scattered string calls"""
    def __init__(self, items_data, ship_db_path, enemy_ships_data):
        self.items_data = items_data
        self.ship_db_path = ship_db_path
        self.enemy_ships_data = enemy_ships_data  # Store the enemy ships list
        self._item_cache = {}
        self._enemy_cache = None

    # Data type constants for clear organization
    DATA_TYPES = {
        'COMBAT_ITEMS': 'Combat',
        'TREASURE_ITEMS': 'Treasure',
        'NAVIGATION_ITEMS': 'Navigation',
        'STORAGE_ITEMS': 'Storage',
        'FOOD_ITEMS': 'Food/Drink'
    }

    def get_items_by_sector(self, sector):
        """Get all items from a specific sector"""
        cache_key = f"sector_{sector}"
        if cache_key not in self._item_cache:
            self._item_cache[cache_key] = [item for item in self.items_data
                                           if item.get('sector') == sector]
        return self._item_cache[cache_key]

    def get_item_by_name(self, item_name):
        """Get specific item data by name with caching"""
        if item_name not in self._item_cache:
            for item in self.items_data:
                if item['name'] == item_name:
                    self._item_cache[item_name] = item
                    break
            else:
                self._item_cache[item_name] = None
        return self._item_cache[item_name]

    def load_enemy_ships(self):
        """Load enemy ships from the Python list (not database)"""
        if self._enemy_cache is not None:
            return self._enemy_cache

        self._enemy_cache = []
        for name, price, base_speed, capacity, sails_multiplier, png in self.enemy_ships_data:
            self._enemy_cache.append({
                "name": name,
                "base_durability": price,  # Price as hull durability
                "base_speed": base_speed,
                "capacity": capacity,
                "sails_multiplier": sails_multiplier,
                "image": f"Assets/{png}",
                "description": f"A hostile {name} prowling the seas.",
                # Pre-calculated combat values
                "base_attack_power": (base_speed * sails_multiplier * capacity) / 10
            })

        return self._enemy_cache

class UnifiedCombatSystem:
    """
    Consolidated combat system that handles both damage calculation and combat logic
    Process Flow:
    1. Load enemy data → 2. Calculate player power → 3. Generate scaled enemy → 4. Simulate battle → 5. Apply results
    """

    def __init__(self, player, data_manager, ui_elements=None):
        self.player = player
        self.data = data_manager
        self.ui = ui_elements or {}
        self.enemy_ships = self.data.load_enemy_ships()

    # === DAMAGE SUBSYSTEM ===
    def apply_damage(self, damage_type, amount):
        """Unified damage application with UI updates"""
        if damage_type == "ship":
            self.player.durability_current = max(0, self.player.durability_current - amount)
            self._update_durability_display()

        return self._check_destruction_status()

    def _update_durability_display(self):
        """Update UI durability display"""
        if "durability_bar" in self.ui:
            percentage = self.player.get_durability_percentage()
            self.ui["durability_bar"].value = percentage
            self.ui["durability_bar"].max_value = 100

    def _check_destruction_status(self):
        """Check if ship is destroyed (5% threshold)"""
        if self.player.get_durability_percentage() <= 5:
            return "ship_sunk", "player_dead"
        return "alive"

    # === COMBAT POWER CALCULATION ===
    def calculate_player_combat_power(self):
        """
        Calculate total combat power from:
        - Fleet ships (speed × capacity × sails)
        - Combat items (effect × quantity)
        - Dehydration penalty (scales from 100% to 20%)
        """
        fleet_power = self._calculate_fleet_power()
        item_bonus = self._calculate_combat_item_bonus()
        dehydration_penalty = self._calculate_dehydration_penalty()

        total_power = (fleet_power + item_bonus) * dehydration_penalty
        return int(max(1, total_power))

    def _calculate_fleet_power(self):
        """Calculate power from all ships in fleet"""
        if not self.player.fleet:
            return 1

        return sum(
            ship.get("base_speed", 1) *
            ship.get("capacity", 1) *
            ship.get("sails_multiplier", 1)
            for ship in self.player.fleet
        )

    def _calculate_combat_item_bonus(self):
        """Calculate bonus from combat items in portfolio"""
        combat_bonus = 0
        combat_items = self.data.get_items_by_sector('Combat')

        for item_name, (quantity, _) in self.player.portfolio.items():
            item_data = self.data.get_item_by_name(item_name)
            if item_data and item_data in combat_items:
                effect_avg = sum(item_data.get("effect", (1, 1))) / 2
                combat_bonus += effect_avg * quantity * 5  # Modest scaling

        return combat_bonus

    def _calculate_dehydration_penalty(self):
        """Calculate penalty from dehydration (100% down to 20%)"""
        return max(0.2, 1 - (self.player.dehydration_awareness / 100))

    # === ENEMY GENERATION SUBSYSTEM ===
    def generate_enemy_ship(self):
        """Generate enemy ship scaled to player's current combat power"""
        player_power = self.calculate_player_combat_power()
        base_enemy = random.choice(self.enemy_ships)

        # Scale enemy relative to player with variability
        scaling_factor = random.uniform(0.7, 1.3)

        enemy_ship = {
            **base_enemy,  # Spread all base properties
            "attack_power": int(base_enemy["base_attack_power"] * scaling_factor),
            "durability": int(base_enemy["base_durability"] * scaling_factor),
            "current_durability": int(base_enemy["base_durability"] * scaling_factor),
            "reward": int((base_enemy["base_attack_power"] + base_enemy["base_durability"]) / 4),
            "loot_chance": random.uniform(0.3, 0.6),
            "cargo": self._generate_enemy_cargo(base_enemy["capacity"]),
            "combat_items": self._generate_enemy_combat_items(base_enemy["base_attack_power"])
        }

        return self._apply_enemy_combat_bonuses(enemy_ship)

    def _generate_enemy_cargo(self, capacity):
        """Fill 50% of enemy capacity with non-combat/treasure items"""
        cargo_capacity = int(capacity / 2)
        available_items = self.data.get_items_by_sector('Combat') + self.data.get_items_by_sector('Treasure')
        available_items = [item for item in self.data.items_data if item not in available_items]

        cargo = {}
        for _ in range(cargo_capacity):
            item = random.choice(available_items)
            cargo[item["name"]] = cargo.get(item["name"], 0) + 1

        return cargo

    def _generate_enemy_combat_items(self, base_strength):
        """Generate 0-3 combat items for enemy ship"""
        combat_items = {}
        num_items = random.randint(0, 3)
        available_combat_items = self.data.get_items_by_sector('Combat')

        for _ in range(num_items):
            item = random.choice(available_combat_items)
            quantity = random.randint(1, 3)
            combat_items[item['name']] = quantity

        return combat_items

    def _apply_enemy_combat_bonuses(self, enemy_ship):
        """Apply combat item bonuses to enemy attack power"""
        combat_multiplier = 1.0

        for item_name, quantity in enemy_ship['combat_items'].items():
            item_data = self.data.get_item_by_name(item_name)
            if item_data:
                effect_avg = sum(item_data.get('effect', (1, 1))) / 2
                combat_multiplier += (effect_avg * quantity * 0.1)  # 10% per item effect

        enemy_ship['attack_power'] = int(enemy_ship['attack_power'] * combat_multiplier)
        return enemy_ship

    # === BATTLE SIMULATION SUBSYSTEM ===
    def simulate_naval_battle(self, enemy_ship):
        """
        Simulate battle with win chance based on power advantage
        Process: Calculate advantage → Determine win chance → Apply damage → Generate rewards
        """
        player_power = self.calculate_player_combat_power()
        enemy_power = enemy_ship["attack_power"]

        advantage = player_power / (enemy_power + 1)
        win_chance = min(95, max(10, advantage * 50))
        victory = random.random() < (win_chance / 100)

        # Damage scales based on victory/defeat
        base_damage = enemy_power * (5 if victory else 10)
        self.apply_damage("ship", int(base_damage))

        return {
            "victory": victory,
            "damage_taken": base_damage,
            "reward": int(enemy_ship["reward"] * (1.0 if victory else 0.25)),
            "loot": self._get_enemy_loot(enemy_ship, victory),
            "player_power": player_power,
            "enemy_power": enemy_power,
            "win_chance": win_chance,
        }

    def _get_enemy_loot(self, enemy_ship, victory):
        """Generate loot from defeated enemy with multiple sources"""
        loot = []

        # Regular loot chance
        if random.random() < enemy_ship['loot_chance']:
            available_items = [item for item in self.data.items_data
                               if item['sector'] != 'Treasure']
            loot.append(random.choice(available_items))

        # Victory bonuses
        if victory:
            # Enemy cargo
            if enemy_ship.get('cargo'):
                for item_name, quantity in enemy_ship['cargo'].items():
                    item_data = self.data.get_item_by_name(item_name)
                    if item_data:
                        loot.extend([item_data] * quantity)

            # Combat items (20% chance)
            if enemy_ship.get('combat_items') and random.random() < 0.2:
                combat_item_name = random.choice(list(enemy_ship['combat_items'].keys()))
                item_data = self.data.get_item_by_name(combat_item_name)
                if item_data:
                    loot.append(item_data)

        return loot

    # === ENCOUNTER HANDLING ===
    def handle_combat_encounter(self, encounter_chance=0.3):
        """Main entry point for combat encounters during sea travel"""
        if random.random() < encounter_chance:
            enemy_ship = self.generate_enemy_ship()
            battle_result = self.simulate_naval_battle(enemy_ship)

            return {
                'encounter': True,
                'enemy_name': enemy_ship['name'],
                'enemy_image': enemy_ship['image'],
                'enemy_description': enemy_ship['description'],
                **battle_result
            }

        return {'encounter': False}

class SEAScreen(Screen):
    def __init__(self, player, **kwargs):
        super().__init__(**kwargs)
        self.player = player
        self.current_enemy = None
        self.enemy_list = []

        # UI and layout setup FIRST
        self.layout = FloatLayout()
        self.item_found_cooldown = False
        self.world_event_cooldown = False
        self.last_event = None

        # --- Background setup ---
        bg = Image(source="Assets/calm_ocean.png", allow_stretch=True, keep_ratio=False)
        self.layout.add_widget(bg)

        # --- Ocean and boat setup ---
        self.ocean = FloatLayout(size_hint=(1, 1))
        self.ocean_canvas = Image(source="Assets/calm_ocean.png", allow_stretch=True, keep_ratio=False)
        self.ocean.add_widget(self.ocean_canvas)

        self.boat = Image(
            source="Assets/side_ship_threequarter_sail.png",
            size_hint=(None, None),
            size=(128, 128)
        )
        self.ocean.add_widget(self.boat)
        self.shadows = []

        self.layout.add_widget(self.ocean)

        # --- CREATE UI ELEMENTS FIRST ---
        self.create_navigation_ui()
        self.create_sea_ui_bars()

        # Add UI elements to layout
        self.layout.add_widget(self.nav_box)

        # --- Title ---
        self.title_image = Image(
            source="Assets/navigating_the_unknown_title_white.png",
            size_hint=(None, None),
            size=(500, 150),
            pos_hint={'center_x': 0.6, 'top': 0.85}
        )
        self.layout.add_widget(self.title_image)

        # --- Back Button ---
        back_btn = Button(
            text="Back to Cargo",
            size_hint=(None, None),
            width=200, height=50,
            pos_hint={'center_x': 0.5, 'y': 0.02}
        )
        back_btn.bind(on_press=self.back_to_user_status)
        self.layout.add_widget(back_btn)

        # === NOW INITIALIZE COMBAT SYSTEM (after UI is created) ===
        self.data_manager = DataManager(
            items_data=items,
            ship_db_path=SHIP_DB_PATH,
            enemy_ships_data=enemy_vessels_data
        )

        self.combat_system = UnifiedCombatSystem(
            player=player,
            data_manager=self.data_manager,
            ui_elements={"durability_bar": self.durability_bar}
        )

        # Combat variables
        self.projectiles = []
        self.enemy_ships = []
        self.sea_monsters = []
        self.cannon_reload_time = 5.0
        self.last_shot_time = 0
        self.combat_mode = False
        self.current_ammo_count = []
        self.max_ammo = 1000
        self.calculate_ammo_from_items()

        # --- Event Manager ---
        self.event_manager = WorldEventManager(
            on_game_over=self.handle_game_over,
            on_excursion=self.handle_excursion,
        )

        # Position variables
        self.heading = 0
        self.latitude = 0.0
        self.longitude = 0.0
        self.boat_x = 100
        self.boat_y = 50

        self.add_widget(self.layout)

        # Bind durability bar to boat position
        self.bind_bar_to_boat()

        # Animation setup
        self.time_elapsed = 0.0
        Clock.schedule_interval(self.animate_title_color, 1 / 6.90)

    def create_navigation_ui(self):
        """Create navigation UI elements."""
        # Navigation Display Box in top left corner
        self.nav_box = BoxLayout(
            orientation='vertical',
            size_hint=(None, None),
            size=(300, 110),
            pos_hint={'x': 0.02, 'top': 0.98},
            spacing=12,
            padding=5
        )

        # Speed display
        self.speed_label = Label(
            text="Speed: 0.0000 knots",
            color=(1, 1, 1, 1),
            font_size='16sp',
            bold=True,
            size_hint_y=0.5
        )

        # Coordinate display
        self.coord_label = Label(
            text="Lat: 0.0000°,\nLon: 0.0000°",
            color=(1, 1, 1, 1),
            font_size='14sp',
            bold=True,
            text_size=(200, None),
            halign='center',
            valign='middle',
        )

        self.nav_box.add_widget(self.speed_label)
        self.nav_box.add_widget(self.coord_label)

        # Add background to nav box
        with self.nav_box.canvas.before:
            Color(0, 0, 0, 0.8)
            self.nav_bg = RoundedRectangle(pos=self.nav_box.pos, size=self.nav_box.size, radius=[5])

        self.nav_box.bind(pos=self._update_nav_bg, size=self._update_nav_bg)

    def create_sea_ui_bars(self):
        """Create ONLY durability bar for SEA screen."""
        current_percentage = self.player.get_durability_percentage() if hasattr(self.player, 'get_durability_percentage') else 100

        # Create VERY thin bar
        self.durability_bar = LayeredBar(
            label_text=f"Fleet: {current_percentage:.1f}%",
            max_value=100,  # Always 100 for percentage
            current_value=current_percentage,
            bar_color=(0.8, 0.8, 0, 1),
            size_hint=(None, None),
            size=(80, 15),  # Width 80px, Total height 15px
            pos=(0, 0)
        )

        self.layout.add_widget(self.durability_bar)

    def calculate_ammo_from_items(self):
        """Calculate ammo based on combat items in cargo"""
        self.max_ammo = 0
        for item_name, quantity in self.player.portfolio.items():
            if "canon" in item_name.lower() or "cannon" in item_name.lower():
                self.max_ammo += quantity * 10  # Each cannon item gives 10 shots
        self.current_ammo_count = self.max_ammo

    def auto_target_and_fire(self, dt=None):
        """Auto-target nearest enemy and fire if conditions are met"""
        if not self.combat_mode or self.current_ammo_count <= 0:
            return

        current_time = time.time()
        if current_time - self.last_shot_time < self.get_reload_time():
            return

        # Find nearest enemy
        nearest_enemy = None
        min_distance = float('inf')

        for enemy in self.enemy_ships:
            enemy_x, enemy_y = enemy['png'].pos
            dx = enemy_x - self.boat_x
            dy = enemy_y - self.boat_y
            distance = math.sqrt(dx * dx + dy * dy)

            if distance < min_distance and distance < 300:  # Max range
                min_distance = distance
                nearest_enemy = enemy

        if nearest_enemy:
            # Calculate accuracy based on dehydration
            accuracy = self.calculate_shot_accuracy()

            # Apply accuracy to target position
            enemy_x, enemy_y = nearest_enemy['widget'].pos
            target_x = enemy_x + 40 + random.uniform(-accuracy, accuracy)
            target_y = enemy_y + 40 + random.uniform(-accuracy, accuracy)

            self.fire_cannon_simple(target_x, target_y)  # Use the simple version
            self.last_shot_time = current_time
            self.current_ammo_count -= 1

    def calculate_shot_accuracy(self):
        """Calculate shot accuracy based on dehydration and combat items"""
        base_accuracy = 50  # pixels of potential miss

        # Dehydration makes aiming harder
        dehydration_penalty = self.player.dehydration_awareness * 2

        # Combat items improve accuracy
        combat_bonus = self.player.get_combat_accuracy_bonus()

        final_accuracy = max(5, base_accuracy - dehydration_penalty + combat_bonus)
        return final_accuracy

    def get_reload_time(self):
        """Calculate reload time based on combat items"""
        base_reload = 5.0  # seconds
        combat_bonus = self.player.get_reload_bonus()  # Implement this in Player
        return max(1.0, base_reload - combat_bonus)

    def bind_bar_to_boat(self):
        def update_bar_position(*args):
            if not hasattr(self, 'boat') or not hasattr(self, 'durability_bar'):
                return

            boat_x, boat_y = self.boat.pos
            boat_w, boat_h = self.boat.size

            # Center horizontally under the boat
            new_x = boat_x + (boat_w / 2) - (self.durability_bar.width / 2)
            new_y = boat_y - 5  # Adjust vertical offset

            # Update bar size and position - keep it thin!
            self.durability_bar.size = (boat_w * 0.7, 12)  # 12px total height, 70% of boat width
            self.durability_bar.pos = (new_x, new_y)

        self.boat.bind(pos=update_bar_position, size=update_bar_position)
        Clock.schedule_once(update_bar_position, 0.05)

    def update_bar_position_smooth(self, *args):
        """Smooth animation for bar position (optional)."""
        if not hasattr(self, 'boat') or not hasattr(self, 'durability_bar'):
            return

        boat_x, boat_y = self.boat.pos
        boat_w, boat_h = self.boat.size
        bar_w, bar_h = self.durability_bar.size

        new_x = boat_x + (boat_w / 2) - (bar_w / 2)
        new_y = boat_y - 5

        Animation.cancel_all(self.durability_bar)
        Animation(pos=(new_x, new_y), duration=0.1).start(self.durability_bar)

    def animate_title_color(self, dt):
        """Apply a smooth rainbow hue shift to the title image."""
        self.time_elapsed += dt
        hue = (math.sin(self.time_elapsed * 2.0) + 1) / 2.0  # oscillate hue between 0-1
        r, g, b = colorsys.hsv_to_rgb(hue, 0.8, 1.0)
        if self.title_image:
            self.title_image.color = (r, g, b, 1)

    def spawn_sea_monster(self, monster_type):
        """Spawn a sea monster boss"""

        print(f"[DEBUG] Spawning Sea Monster: {monster_type if isinstance(monster_type, str) else 'UNKNOWN'}")

        monster_data = {
            "kraken": {
                "name": "Kraken",
                "png": "kraken_monster.png",
                "durability": 500000,
                "attack_pattern": "tentacle_slam",
                "special_ability": "ink_cloud",
                "loot_multiplier": 5.0
            },
            "leviathan": {
                "name": "Leviathan",
                "png": "leviathan_monster.png",
                "durability": 800000,
                "attack_pattern": "charge",
                "special_ability": "tsunami_wave",
                "loot_multiplier": 8.0
            }
        }

        if monster_type in monster_data:
            data = monster_data[monster_type]
            monster = {
                'widget': Image(
                    source=f"Assets/{data['png']}",
                    size_hint=(None, None),
                    size=(150, 150),  # Larger than ships
                    pos=(self.boat_x + 200, self.boat_y + 200)  # Spawn near player
                ),
                'data': data,
                'current_durability': data['durability'],
                'max_durability': data['durability'],
                'attack_cooldown': 0
            }
            self.ocean.add_widget(monster['widget'], index=len(self.ocean.children))
            self.sea_monsters.append(monster)
            self.show_popup("Sea Monster!", f"A {data['name']} appears!")

            # Start monster AI
            Clock.schedule_interval(lambda dt: self.update_monster_behavior(monster), 0.5)

    def update_monster_behavior(self, monster):
        """Update sea monster AI and attacks"""
        if monster not in self.sea_monsters:
            return False  # Stop scheduling if monster is dead

        monster['attack_cooldown'] -= 0.5

        if monster['attack_cooldown'] <= 0:
            self.monster_attack(monster)
            monster['attack_cooldown'] = random.uniform(3.0, 8.0)

        return True

    # Add these missing sea monster attack methods:
    def spawn_tentacle_attack(self, x, y):
        """Spawn a tentacle attack at specified position"""
        try:
            tentacle = Image(
                source="Assets/tentacle.png",  # You'll need this asset
                size_hint=(None, None),
                size=(60, 100),
                pos=(x, y)
            )
            self.ocean.add_widget(tentacle)

            # Animate tentacle
            anim = Animation(opacity=1, duration=0.5) + Animation(opacity=0, duration=0.5)
            anim.start(tentacle)
            Clock.schedule_once(lambda dt: self.ocean.remove_widget(tentacle), 1.0)

        except Exception as e:
            print(f"Error spawning tentacle: {e}")

    def monster_charge_attack(self, monster):
        """Handle monster charge attack"""
        try:
            # Move monster toward player
            monster_x, monster_y = monster['widget'].pos
            dx = self.boat_x - monster_x
            dy = self.boat_y - monster_y
            distance = math.sqrt(dx * dx + dy * dy)

            if distance > 0:
                monster['widget'].x += (dx / distance) * 10
                monster['widget'].y += (dy / distance) * 10

        except Exception as e:
            print(f"Error in charge attack: {e}")

    def monster_attack(self, monster):
        """Sea monster performs an attack"""
        attack_type = monster['data']['attack_pattern']

        if attack_type == "tentacle_slam":
            # Spawn multiple tentacles around player
            for i in range(3):
                tentacle_x = self.boat_x + random.uniform(-100, 100)
                tentacle_y = self.boat_y + random.uniform(-100, 100)
                self.spawn_tentacle_attack(tentacle_x, tentacle_y)

        elif attack_type == "charge":
            # Monster charges toward player
            self.monster_charge_attack(monster)

    def _update_nav_bg(self, instance, value):
        """Update navigation background rectangle position and size."""
        if hasattr(self, "nav_bg"):
            self.nav_bg.pos = instance.pos
            self.nav_bg.size = instance.size

    def update_durability_display(self):
        """Update durability bar display with percentage."""
        if hasattr(self, 'durability_bar') and hasattr(self.player, 'get_durability_percentage'):
            percentage = self.player.get_durability_percentage()
            self.durability_bar.current_value = percentage
            self.durability_bar.label_text = f"Fleet: {percentage:.1f}%"

            # Update bar color based on durability level
            if percentage > 70:
                self.durability_bar.bar_color = (0, 0.8, 0, 1)  # Green
            elif percentage > 30:
                self.durability_bar.bar_color = (0.8, 0.8, 0, 1)  # Yellow
            else:
                self.durability_bar.bar_color = (0.8, 0, 0, 1)  # Red

            # Force UI update if available
            if hasattr(self.durability_bar, 'update_display'):
                self.durability_bar.update_display()

    def update_durability_stats(self):
        """Update durability stats from fleet."""
        if getattr(self.player, "fleet", None) and len(self.player.fleet) > 0:
            self.player.durability_current = sum(
                ship.get("durability_current", 100) for ship in self.player.fleet) / len(self.player.fleet)
            self.player.durability_max = sum(
                ship.get("durability_max", 100) for ship in self.player.fleet) / len(self.player.fleet)
        else:
            self.player.durability_current = 100
            self.player.durability_max = 100

        # Update the bar display
        self.update_durability_display()

    def on_enter(self):
        """Called when screen is entered."""
        # Update player's fleet stats
        if hasattr(self.player, 'update_fleet_stats'):
            self.player.update_fleet_stats()

        # Update UI displays
        self.update_durability_stats()
        self.update_speed_display()
        self.update_navigation_display()

        # Calculate navigation-based timing
        nav_bonus = self.player.get_navigation_bonus()
        effective_bonus = min(nav_bonus / 10, 0.6)
        interval = max(1.0, 5.0 * (1 - effective_bonus))
        populate_ships()

        print(f"DEBUG: Navigation bonus = {nav_bonus:.4f}% -> Interval = {interval:.4f}s")

        if not self.player.fleet:
            self.show_no_ship_popup()
            return

        def delayed_init(dt):
            try:
                self.boat_x = self.layout.width / 2 - self.boat.width / 2
                self.boat_y = self.layout.height / 2 - self.boat.height / 2
                self.boat.pos = (self.boat_x, self.boat_y)
                self.update_speed_display()
                self.update_navigation_display()

            except Exception as e:
                print(f"ERROR in delayed_init: {e}")

        Clock.schedule_once(delayed_init, 0.1)

        # === CONSOLIDATED EVENT SCHEDULING ===
        Window.bind(on_key_down=self.on_key_down)

        # Core update loops
        Clock.schedule_interval(self.update_boat_position, 1 / 60)
        Clock.schedule_interval(self.check_collisions, 1 / 60)
        Clock.schedule_interval(self.update_projectiles, 1/60)  # 60 FPS
        Clock.schedule_interval(self.spawn_wave, 1)
        Clock.schedule_interval(self.spawn_shadow, 5)
        Clock.schedule_interval(self.apply_drift, 0.01)

        # Combat-related scheduling
        Clock.schedule_interval(self.check_combat_encounters, 10)
        Clock.schedule_interval(self.auto_target_and_fire, 0.1)  # Auto-firing

        Clock.schedule_interval(self.spawn_enemy_ship, 15)
        Clock.schedule_interval(self.spawn_sea_monster, 20)  # Less frequent for bosses

        # Dynamic navigation update speed
        Clock.schedule_interval(self.update_navigation_display, interval)

    def spawn_enemy_ship(self, dt):
        """Spawn an enemy ship with combat capabilities"""
        try:
            ocean_w, ocean_h = self.ocean.size
            enemy_size = 80

            # Get random enemy ship data
            enemy_data = random.choice(enemy_vessels_data)
            name, price, speed, capacity, sail_multiplier, png = enemy_data

            if not self.current_enemy:
                self.current_enemy = enemy_vessels_data

            # Find spawn position (away from player)
            for _ in range(10):
                x = random.randint(100, int(ocean_w - enemy_size - 100))
                y = random.randint(100, int(ocean_h - enemy_size - 100))

                dx = x - self.boat_x
                dy = y - self.boat_y
                dist = math.sqrt(dx * dx + dy * dy)

                if dist > 200:  # Minimum spawn distance
                    break
            else:
                return

            # Create enemy ship
            enemy = {
                'widget': Image(
                    source=f"Assets/{png}",
                    size_hint=(None, None),
                    size=(enemy_size, enemy_size),
                    pos=(x, y)
                ),
                'data': enemy_data,
                'current_durability': capacity * 10,  # Base durability
                'max_durability': capacity * 10,
                'cannon_count': max(1, capacity // 10),  # Rough cannon estimate
                'reload_time': 7.0,
                'last_shot': 0,
                'speed': speed * 0.3  # Slower than player for balance
            }

            self.ocean.add_widget(enemy['widget'])
            self.enemy_ships.append(enemy)

            print(f"Enemy {name} spawned at ({x}, {y})")

        except Exception as e:
            print(f"Error spawning enemy: {e}")

    def fire_cannon(self, target_x, target_y, is_player=True):
        """Fire a cannonball toward target coordinates"""
        try:
            if is_player:
                source_x, source_y = self.boat_x + 40, self.boat_y + 40  # Player boat center
                damage = self.calculate_player_damage()
                shooter = "player"
            else:
                # Enemy firing at player
                if not self.current_enemy:
                    return
                enemy = self.current_enemy
                source_x, source_y = enemy['widget'].x + 40, enemy['widget'].y + 40
                damage = 8  # Slightly weaker than player
                shooter = "enemy"

            # Create cannonball
            cannonball = Image(
                source="Assets/cannon_shot_round.png",
                size_hint=(None, None),
                size=(20, 20),
                pos=(source_x, source_y)
            )

            # Calculate trajectory
            dx = target_x - source_x
            dy = target_y - source_y
            distance = math.sqrt(dx * dx + dy * dy)
            if distance > 0:
                dx, dy = dx / distance, dy / distance

            projectile_data = {
                'widget': cannonball,
                'dx': dx * 8,
                'dy': dy * 8,
                'damage': damage,
                'shooter': shooter,
                'distance_traveled': 0,
                'max_range': 300
            }

            self.ocean.add_widget(cannonball)
            self.projectiles.append(projectile_data)
            self.animate_muzzle_flash(source_x, source_y)

        except Exception as e:
            print(f"Error firing cannon: {e}")

    def calculate_player_damage(self):
        """Calculate damage based on player's combat items"""
        base_damage = 10
        combat_bonus = self.player.get_combat_bonus()  # You'll need to implement this
        return base_damage * (1 + combat_bonus / 100)

    def animate_muzzle_flash(self, x, y):
        """Show muzzle flash animation"""
        flash = Image(
            source="Assets/muzzle_flash.png",
            size_hint=(None, None),
            size=(30, 30),
            pos=(x - 5, y - 5)
        )
        self.ocean.add_widget(flash)

        Animation(opacity=0, duration=0.3).start(flash)
        Clock.schedule_once(lambda dt: self.ocean.remove_widget(flash), 0.3)

    def update_projectiles(self, dt):
        """Update all active projectiles"""
        projectiles_to_remove = []

        for proj in self.projectiles:
            widget = proj['widget']

            # Move projectile
            widget.x += proj['dx']
            widget.y += proj['dy']
            proj['distance_traveled'] += math.sqrt(proj['dx'] ** 2 + proj['dy'] ** 2)

            # Check range limit
            if proj['distance_traveled'] > proj['max_range']:
                projectiles_to_remove.append(proj)
                continue

            # Check collisions
            if self.check_projectile_collision(proj):
                projectiles_to_remove.append(proj)

        # Remove old projectiles
        for proj in projectiles_to_remove:
            self.ocean.remove_widget(proj['widget'])
            self.projectiles.remove(proj)

    def check_projectile_collision(self, projectile):
        """Check if projectile hit something"""
        proj_x, proj_y = projectile['widget'].pos
        proj_size = 20

        if projectile['shooter'] == "player":
            # Check against enemy ships
            for enemy in self.enemy_ships:
                enemy_x, enemy_y = enemy['widget'].pos
                enemy_size = 80

                if (proj_x < enemy_x + enemy_size and proj_x + proj_size > enemy_x and
                        proj_y < enemy_y + enemy_size and proj_y + proj_size > enemy_y):
                    # Hit! Apply damage
                    self.apply_damage(enemy, projectile['damage'])
                    self.show_damage_effect(enemy_x, enemy_y)
                    return True

        return False

    def apply_damage(self, enemy, damage):
        """Apply damage to enemy ship"""
        enemy['current_durability'] -= damage

        # Visual feedback
        enemy['widget'].canvas.before.clear()
        with enemy['widget'].canvas.before:
            Color(1, 0, 0, 0.3)  # Red flash
            Rectangle(pos=enemy['widget'].pos, size=enemy['widget'].size)

        Clock.schedule_once(lambda dt: self.clear_damage_effect(enemy['widget']), 0.2)

        # Check if ship is defeated
        if enemy['current_durability'] <= 0:
            self.defeat_enemy(enemy)

    def clear_damage_effect(self, widget):
        """Clear damage visual effect"""
        widget.canvas.before.clear()

    def show_damage_effect(self, x, y):
        """Show explosion/splash effect"""
        explosion = Image(
            source="Assets/explosion.png",
            size_hint=(None, None),
            size=(40, 40),
            pos=(x + 20, y + 20)
        )
        self.ocean.add_widget(explosion)

        anim = Animation(opacity=0, duration=0.5)
        anim.start(explosion)
        Clock.schedule_once(lambda dt: self.ocean.remove_widget(explosion), 0.5)

    def defeat_enemy(self, enemy):
        """Handle defeated enemy ship"""
        # Calculate loot based on capture (not sinking)
        base_loot = enemy['data'][1] // 10  # 10% of ship value
        capture_bonus = base_loot * 2  # Double for capture

        # Remove enemy
        self.ocean.remove_widget(enemy['widget'])
        self.enemy_ships.remove(enemy)

        # Award loot
        self.player.gold += capture_bonus

        # Show victory message
        self.show_popup("Victory!",
                        f"Enemy {enemy['data'][0]} captured!\n"
                        f"Gold earned: {capture_bonus}")

    def enemy_fire_at_player(self, enemy):
        """Enemy ship fires at player and then does a small reposition (recoil/maneuver)."""
        try:
            # get enemy's widget and position
            enemy_w = enemy['widget']
            enemy_x, enemy_y = enemy_w.pos
            # use a firing origin near the center of the enemy sprite
            source_x = enemy_x + (enemy_w.width / 2)
            source_y = enemy_y + (enemy_w.height / 2)

            # target is player's boat center
            target_x = self.boat_x + (self.boat.width / 2)
            target_y = self.boat_y + (self.boat.height / 2)

            # add some inaccuracy based on enemy stats or random spread
            inaccuracy_x = random.uniform(-20, 20)
            inaccuracy_y = random.uniform(-20, 20)
            aim_x = target_x + inaccuracy_x
            aim_y = target_y + inaccuracy_y

            # calculate damage (you can use enemy['cannon_count'] or other stat)
            base_enemy_damage = max(5, int(enemy.get('cannon_count', 1) * 8))

            # Spawn projectile from enemy
            self.fire_cannon(source_x, source_y, aim_x, aim_y, damage=base_enemy_damage, shooter="enemy")

            # record last_shot timestamp for enemy to control reloads
            enemy['last_shot'] = time.time()

            # Small reposition after firing: either recoil or tactical strafe
            # Move the enemy a few pixels perpendicular to the shot direction for a believable effect
            dx = aim_x - source_x
            dy = aim_y - source_y
            dist = math.hypot(dx, dy) or 1.0
            # perpendicular vector (normalized)
            px, py = -dy / dist, dx / dist
            maneuver_strength = random.uniform(5.0, 15.0)  # pixels to move
            # randomly choose left/right strafe
            side = 1 if random.random() < 0.5 else -1
            enemy_w.x += px * maneuver_strength * side
            enemy_w.y += py * maneuver_strength * side

            # Clamp inside ocean area to avoid moving off-screen
            enemy_w.x = max(0, min(self.ocean.width - enemy_w.width, enemy_w.x))
            enemy_w.y = max(0, min(self.ocean.height - enemy_w.height, enemy_w.y))

        except Exception as e:
            print(f"Error in enemy_fire_at_player: {e}")

    def toggle_combat_mode(self, active):
        """Toggle combat mode on/off"""
        self.combat_mode = active
        if active:
            print("Combat mode activated!")
            # Start enemy spawning
            Clock.schedule_interval(self.spawn_enemy_ship, 30)  # Every 30 seconds
            Clock.schedule_interval(self.update_enemy_behavior, 0.1)
            Clock.schedule_interval(self.update_projectiles, 0.016)
        else:
            print("Combat mode deactivated")
            # Clean up enemies
            for enemy in self.enemy_ships[:]:
                self.ocean.remove_widget(enemy['widget'])
            self.enemy_ships.clear()

    def update_enemy_behavior(self, dt):
        """Update enemy ship AI and firing"""
        current_time = time.time()  # FIXED: Use time.time() not dt.time()

        for enemy in self.enemy_ships:
            # Simple AI: move toward player and fire when in range
            enemy_x, enemy_y = enemy['widget'].pos
            dx = self.boat_x - enemy_x
            dy = self.boat_y - enemy_y
            distance = math.sqrt(dx * dx + dy * dy)

            # Move toward player if far away
            if distance > 150:
                if distance > 0:
                    enemy['widget'].x += (dx / distance) * enemy['speed']
                    enemy['widget'].y += (dy / distance) * enemy['speed']

            # Fire at player if in range and reloaded
            if (distance < 200 and
                    current_time - enemy['last_shot'] > enemy['reload_time']):
                self.enemy_fire_at_player(enemy)
                enemy['last_shot'] = current_time

    def on_touch_down(self, touch):
        """Handle touch input for cannon firing"""
        if self.combat_mode and self.can_fire():
            self.fire_cannon_simple(touch.x, touch.y)  # Use simple version for touch
            self.last_shot_time = time.time()
        return super().on_touch_down(touch)

    def can_fire(self):
        """Check if player can fire cannon (reload time)"""
        return time.time() - self.last_shot_time >= self.cannon_reload_time

    def update_reload_display(self, dt):
        """Update reload progress bar"""
        if self.combat_mode:
            reload_progress = time.time() - self.last_shot_time  # FIXED: Use time.time()
            # You'll need to create this reload_bar in your UI first
            if hasattr(self, 'reload_bar'):
                self.reload_bar.value = min(reload_progress, self.cannon_reload_time)

    def update_navigation_display(self, dt=None):
        """Update coordinate and speed display."""
        try:
            nav_bonus = self.player.get_navigation_bonus()
            self.coord_label.text = f"Lat: {self.latitude:.4f}°, \nLon: {self.longitude:.4f}° \n(Nav +{nav_bonus:.4f}%)"
            self.update_speed_display()
        except Exception as e:
            print(f"Error updating navigation display: {e}")

    def update_speed_display(self):
        """Update the speed label with current speed"""
        try:
            speed = getattr(self.player, 'speed', 0)
            self.speed_label.text = f"Speed: {speed:.4f} knots"
        except Exception as e:
            print(f"Error updating speed display: {e}")

    def handle_item_found(self, item):
        if self.item_found_cooldown:
            print("Item found ignored — cooldown active")
            return
        self.item_found_cooldown = True
        Clock.schedule_once(lambda dt: setattr(self, "item_found_cooldown", False), 1.0)

        try:
            if isinstance(item, dict):
                item_name = item['name']
                description = item.get('description', 'A mysterious item')
            else:
                item_name = item
                description = "A valuable find!"

            success, message = self.player.add_item(item_name)
            text = f"{item_name}: {description}\n{message}"

            # Use a BoxLayout with a Label that wraps text
            content = BoxLayout(orientation='vertical', padding=10, spacing=10)
            label = Label(text=text, halign='center', valign='top', text_size=(400, None))
            label.bind(texture_size=label.setter('size'))  # Auto-size height
            content.add_widget(label)

            close_btn = Button(text="Continue", size_hint_y=None, height=50)
            content.add_widget(close_btn)

            popup = Popup(title="Treasure Found!", content=content, size_hint=(0.7, None))
            popup.height = min(500, label.height + 100)  # Fit label
            close_btn.bind(on_press=popup.dismiss)
            popup.open()

        except Exception as e:
            print(f"Error handling found item: {e}")

    def show_no_ship_popup(self):
        """Show popup if player has no ship and return to previous screen."""
        popup = Popup(
            title="No Ship!",
            content=Label(text="You need a ship to sail the seas!\nVisit the Shipwright first."),
            size_hint=(0.6, 0.4)
        )
        popup.bind(on_dismiss=lambda x: setattr(self.manager, 'current', 'user_status_screen'))
        popup.open()

    def update_boat_position(self, dt):
        """Update boat position based on player speed and heading."""
        try:
            # Only move if speed > 0
            if self.player.speed <= 0:
                return

            self.nav_bonus = self.player.get_navigation_bonus()
            angle = math.radians(self.player.heading)
            move_scale = 0.01
            self.boat_x += math.cos(angle) * self.player.speed * self.nav_bonus * dt * move_scale
            self.boat_y += math.sin(angle) * self.player.speed * self.nav_bonus * dt * move_scale

            if self.nav_bonus > 55:
                # Apply a controlled acceleration curve (e.g., square root or mild exponential)
                extra_scale = (self.nav_bonus - 55) / 45  # normalize 55–100% range to 0–1
                move_scale *= 1 + (extra_scale * 0.5)

            # Screen wrapping and latitude/longitude update
            margin = 10
            if (self.boat_x < margin or self.boat_x > self.width - margin or
                    self.boat_y < margin or self.boat_y > self.height - margin):
                self.boat_x = self.width / 2
                self.boat_y = self.height / 2
                self.latitude += math.sin(angle) * 2.0
                self.longitude += math.cos(angle) * 2.0
                self.update_ocean_background()

            self.boat.pos = (self.boat_x, self.boat_y)

        except Exception as e:
            print(f"Error in boat position update: {e}")

    def check_world_event(self):
        """Unified event check — works with collisions and item_found."""
        if getattr(self, "world_event_cooldown", False):
            return

        try:
            result = self.event_manager.check_events(self.latitude, self.longitude)
            if result and result != getattr(self, "last_event", None):
                print(f"DEBUG: Triggered world event: {result}")

                # Stop the ship
                self.player.speed = 0

                if result == "item_found":
                    if hasattr(self, "handle_item_found") and callable(self.handle_item_found):
                        item = self.event_manager.pick_random_item(items)
                        self.handle_item_found(item)
                    else:
                        print("DEBUG: handle_item_found not callable")

                self.last_event = result

                # Start cooldown
                self.world_event_cooldown = True
                Clock.schedule_once(lambda dt: setattr(self, "world_event_cooldown", False), 1.0)

        except Exception as e:
            print(f"Error in event check: {e}")

    def check_combat_encounters(self, dt):
        """Check for combat encounters during travel."""
        try:
            # Only check if moving
            if self.player.speed > 0:
                combat_result = self.combat_system.handle_combat_encounter()

                if combat_result['encounter']:
                    self.handle_combat_result(combat_result)

        except Exception as e:
            print(f"Error in combat encounter: {e}")

    def check_collisions(self, dt):
        """Check for collisions between boat and shadows."""
        try:
            # Smaller hitbox for more precise collision
            hitbox_scale = 0.1  # 50% of boat size
            bx, by = self.boat.pos
            bw, bh = self.boat.size
            offset_x = (1 - hitbox_scale) * bw / 50
            offset_y = (1 - hitbox_scale) * bh / 50
            boat_rect = (bx + offset_x, by + offset_y, bw * hitbox_scale, bh * hitbox_scale)

            for shadow in self.shadows[:]:
                sx, sy = shadow.pos
                sw, sh = shadow.size
                shadow_rect = (sx, sy, sw, sh)

                if self.rect_overlap(boat_rect, shadow_rect):
                    print("DEBUG: Shadow collision detected! Triggering item_found.")

                    # Stop the ship immediately
                    self.player.speed = 0

                    # Trigger event safely
                    if hasattr(self, "handle_item_found") and callable(self.handle_item_found):
                        item = self.event_manager.pick_random_item(items)
                        self.handle_item_found(item)

                    # Remove shadow
                    self.remove_shadow(shadow)

                    # Cooldown
                    self.world_event_cooldown = True
                    Clock.schedule_once(lambda dt: setattr(self, "world_event_cooldown", False), 1.0)

                    self.last_event = "item_found"
                    break

        except Exception as e:
            print(f"Error in collision check: {e}")

    def handle_combat_result(self, combat_result):
        """Handle and display combat results."""
        enemy_name = combat_result['enemy_name']
        victory = combat_result['victory']
        damage_taken = combat_result['damage_taken']
        reward = combat_result['reward']

        # Stop the ship during combat
        self.player.speed = 0

        # Update gold reward
        self.player.gold += reward

        # Update durability display
        self.update_durability_display()

        # Create combat popup - show percentage instead of raw numbers
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)

        durability_percent = self.player.get_durability_percentage()

        if victory:
            title = "Victory!"
            message = f"You defeated the {enemy_name}!\nDamage taken: {damage_taken:,}\nFleet Integrity: {durability_percent:.1f}%\nReward: ${reward:,}"
        else:
            title = "Defeat!"
            message = f"You lost to the {enemy_name}!\nDamage taken: {damage_taken:,}\nFleet Integrity: {durability_percent:.1f}%\nConsolation: ${reward:,}"

        content.add_widget(Label(text=message, halign='center'))

        # Add loot if any
        if combat_result.get('loot'):
            for loot_item in combat_result['loot']:
                self.player.add_item(loot_item['name'])
            loot_text = "Loot obtained:\n" + "\n".join([item['name'] for item in combat_result['loot']])
            content.add_widget(Label(text=loot_text, halign='center'))

        close_btn = Button(text="Continue", size_hint_y=None, height=50)
        content.add_widget(close_btn)

        popup = Popup(title=title, content=content, size_hint=(0.7, 0.5))
        close_btn.bind(on_press=popup.dismiss)

        # Check if ship was destroyed (using percentage threshold)
        if combat_result.get('damage_result') == 'ship_sunk':
            popup.bind(on_dismiss=lambda x: self.handle_game_over("Your ship was destroyed in battle!"))

        popup.open()

    def spawn_wave(self, dt):
        try:
            wave = Image(
                source="Assets/wave.png",
                size_hint=(None, None),
                size=(self.width * 4, Window.height * 4),
                pos=(random.randint(0, int(self.width)), random.randint(0, int(self.height)))
            )
            self.ocean.add_widget(wave)

            # Animate wave movement
            move_distance = 400
            angle_rad = math.radians(self.player.heading)
            dx = math.cos(angle_rad) * move_distance
            dy = math.sin(angle_rad) * move_distance

            anim = Animation(x=wave.x + dx, y=wave.y + dy, duration=9, opacity=0.5) + Animation(opacity=0.9, duration=4)
            anim.bind(on_complete=lambda *a: self.ocean.remove_widget(wave))
            anim.start(wave)

        except Exception as e:
            print(f"Error spawning wave: {e}")

    def launch_mini_game(self):
        """Launch a random mini-game after successful excursion."""
        from minigames import (
            CanonBlastMiniGame, PodiumMiniGame, CanonLoaderMiniGame,
            SeaBattleMiniGame, SabotageMiniGame,
            PearlDiverMiniGame, DiceRollingMiniGame
        )

        games = [
            ("Canon Blast", "canon", CanonBlastMiniGame),
            ("Podium", "podium", PodiumMiniGame),
            ("Canon Loader", "canon_loader", CanonLoaderMiniGame),
            ("Sea Battle", "sea_battle", SeaBattleMiniGame),
            ("Sabotage", "sabotage", SabotageMiniGame),
            ("Pearl Diver", "pearl_diver", PearlDiverMiniGame),
            ("Dice Rolling", "dice_rolling", DiceRollingMiniGame)
        ]

        title, name, cls = random.choice(games)

    def spawn_shadow(self, dt=None):
        """Spawn a shadow obstacle at a random position away from the boat."""
        try:
            # Delay first spawn slightly so boat is positioned
            if not hasattr(self, "_initialized_shadows"):
                self._initialized_shadows = True
                return  # skip first call, schedule will call again later

            # Use the ocean layout size for coordinates
            ocean_w, ocean_h = self.ocean.size
            shadow_size = 70
            min_distance = 10  # distance from ship on spawn

            # Try up to 10 times to find a non-colliding position
            for _ in range(10):
                x = random.randint(0, int(ocean_w - shadow_size))
                y = random.randint(0, int(ocean_h - shadow_size))

                dx = x - self.boat_x
                dy = y - self.boat_y
                dist = math.sqrt(dx * dx + dy * dy)

                if dist > min_distance:
                    break
            else:
                return  # couldn’t find a good spot

            shadow = Image(
                source="Assets/shadow.png",
                size_hint=(None, None),
                size=(shadow_size, shadow_size),
                pos=(x, y),
                opacity=0
            )

            self.ocean.add_widget(shadow)
            self.shadows.append(shadow)

            anim = Animation(opacity=1, duration=2.5) + Animation(opacity=0.3, duration=3.5)
            anim.repeat = True
            anim.start(shadow)

            # Remove after 12s
            Clock.schedule_once(lambda dt: self.remove_shadow(shadow), 25)

        except Exception as e:
            print(f"Error spawning shadow: {e}")

    def apply_drift(self, dt):
        """Apply drift effect based on dehydration. Accepts dt parameter from Clock."""
        try:
            if self.player.dehydration_awareness < 5:
                return  # no drift yet

            drift_strength = (self.player.dehydration_awareness - 5) * 0.15  # Reduced effect
            self.boat_x += random.uniform(-drift_strength, drift_strength)
            self.boat_y += random.uniform(-drift_strength, drift_strength)
            self.boat.pos = (self.boat_x, self.boat_y)
        except Exception as e:
            print(f"Error applying drift: {e}")

    def remove_shadow(self, shadow):
        if shadow in self.shadows:
            self.ocean.remove_widget(shadow)
            self.shadows.remove(shadow)

    def handle_excursion(self, name, description):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=description, halign='center'))

        btn_play = Button(text="Play Mini-Game", size_hint_y=None, height=50)
        btn_skip = Button(text="Skip", size_hint_y=None, height=50)
        content.add_widget(btn_play)
        content.add_widget(btn_skip)

        popup = Popup(title=f"Adventure: {name}", content=content, size_hint=(0.7, 0.5))
        btn_play.bind(on_press=lambda x: (self.launch_mini_game(), popup.dismiss()))
        btn_skip.bind(on_press=popup.dismiss)
        popup.open()

    def handle_game_over(self, description):
        """Handle game over scenario."""
        self.show_popup("Disaster!", description)
        # Transition to game over screen
        go_screen = self.manager.get_screen("game_over")
        go_screen.finalize(self.player, description)
        self.manager.current = "game_over"

    def show_popup(self, title, message):
        """Show a simple popup message."""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=message, halign='center'))

        close_btn = Button(text="Continue", size_hint_y=None, height=50)
        content.add_widget(close_btn)

        popup = Popup(title=title, content=content, size_hint=(0.7, 0.5))
        close_btn.bind(on_press=popup.dismiss)
        popup.open()

    def on_key_down(self, window, key, scancode, codepoint, modifiers):
        """Handle keyboard controls for ship movement."""
        # Up arrow or W - increase speed
        if key in (273, 119):
            self.player.speed = min(self.player.max_speed, self.player.speed + 5)
            self.update_speed_display()
            self.update_navigation_display()
            print(f"Speed increased to: {self.player.speed}")

        # Down arrow or S - decrease speed
        elif key in (274, 115):
            self.player.speed = max(1, self.player.speed - 5)
            self.update_speed_display()
            self.update_navigation_display()
            print(f"Speed decreased to: {self.player.speed}")

        # Left arrow or A - turn left
        elif key in (276, 97):
            self.player.heading += 9
            print(f"Heading: {self.player.heading}°")

        # Right arrow or D - turn right
        elif key in (275, 100):
            self.player.heading -= 9
            print(f"Heading: {self.player.heading}°")

    def back_to_user_status(self, instance=None):
        """Return to user status screen."""
        # Stop all scheduled events
        Clock.unschedule(self.update_boat_position)
        Clock.unschedule(self.check_collisions)
        Clock.unschedule(self.spawn_wave)
        Clock.unschedule(self.apply_drift)
        Clock.unschedule(self.spawn_sea_monster)
        Clock.unschedule(self.check_combat_encounters)

        Clock.unschedule(self.update_speed_display)
        Window.unbind(on_key_down=self.on_key_down)

        # Advance time and update displays
        user_screen = self.manager.get_screen("user_status_screen")
        user_screen.advance_time(hours=2)  # 2 hours of sailing
        user_screen.update_time_display()

        self.manager.current = "user_status_screen"

    def on_pre_enter(self):
        """Bind keys when screen is about to be entered."""
        Window.bind(on_key_down=self.on_key_down)

    def on_pre_leave(self):
        """Unbind keys when leaving screen."""
        Window.unbind(on_key_down=self.on_key_down)
        # Clean up scheduled events
        Clock.unschedule(self.spawn_shadow)
        Clock.unschedule(self.update_boat_position)
        Clock.unschedule(self.check_collisions)
        Clock.unschedule(self.spawn_wave)
        Clock.unschedule(self.apply_drift)
        Clock.unschedule(self.update_navigation_display)
        Clock.unschedule(self.show_navigation_breakdown())

    def show_navigation_breakdown(self):
        self.player.print_detailed_navigation_bonuses()

    def update_ocean_background(self):
        """Update ocean background based on latitude."""
        self.update_navigation_display()
        for region in OCEAN_REGIONS:
            if region["lat_range"][0] <= self.latitude <= region["lat_range"][1]:
                new_image = region["image"]
                if self.ocean_canvas.source != new_image:
                    self.ocean_canvas.source = new_image
                    print(f"Now entering: {region['name']}")
                break

    @staticmethod
    def rect_overlap(a, b):
        ax, ay, aw, ah = a
        bx, by, bw, bh = b
        return (ax < bx + bw and ax + aw > bx and ay < by + bh and ay + ah > by)

class GameOverScreen(Screen):
    def __init__(self, sm, **kwargs):
        super().__init__(**kwargs)
        self.sm = sm
        # FloatLayout for layering background + UI
        self.layout = FloatLayout()
        # Background image
        bg = Image(source="Assets/monster_map.png", allow_stretch=True, keep_ratio=False)
        self.layout.add_widget(bg)

        # Foreground UI layout (centered box for text only)
        ui_layout = BoxLayout(
            orientation='vertical',
            spacing=20,
            padding=20,
            size_hint=(0.8, 0.6),
            pos_hint={'center_x': 0.5, 'center_y': 0.6}
        )

        # Top message (cause of failure)
        self.failure_label = Label(text="", font_size=18, halign="center")
        ui_layout.add_widget(self.failure_label)

        # Stats
        self.stats_label = Label(text="", font_size=16, halign="center")
        ui_layout.add_widget(self.stats_label)

        # Executor message
        self.message = Label(
            text="The fates of the ocean gained control of your assets.",
            font_size=14,
            halign="center"
        )
        ui_layout.add_widget(self.message)

        # Add the text layout to the root
        self.layout.add_widget(ui_layout)

        # Bottom button row
        btn_layout = BoxLayout(
            orientation='horizontal',
            size_hint=(0.9, None),  # 90% wide, fixed height
            height=50,
            spacing=20,
            pos_hint={'center_x': 0.5, 'y': 0.05}  # centered at bottom
        )

        # Exit button (red)
        exit_btn = Button(
            text="Exit",
            size_hint=(None, 1),
            width=200,
            background_normal='',  # remove default image
            background_color=(0.8, 0, 0, 1)  # RGBA -> pure red
        )
        exit_btn.bind(on_press=self.exit_game)
        btn_layout.add_widget(exit_btn)

        # Restart button (green)
        restart_btn = Button(
            text="Restart",
            size_hint=(None, 1),
            width=200,
            background_normal='',  # remove default image
            background_color=(0, 0.7, 0, 1)  # RGBA -> pure green
        )
        restart_btn.bind(on_press=self.restart_game)
        btn_layout.add_widget(restart_btn)
        # Add button row to root
        self.layout.add_widget(btn_layout)

        self.add_widget(self.layout)

    def finalize(self, player, reason="", items=None):
        # Failure cause description
        self.failure_label.text = f"{reason}\n\n"
        # item summary
        if player.portfolio:
            item_summary_lines = []
            for name, (units, total_cost) in player.portfolio.items():
                avg_price = total_cost / units if units > 0 else 0
                line = f"{name}: {units} units @ ${avg_price:.2f}"

                # Optionally add current market price if `items` provided
                if items:
                    current_price = next((s['price'] for s in items if s['name'] == name), avg_price)
                    line += f" = ${current_price * units:.2f}"
                item_summary_lines.append(line)

            item_summary = "\n".join(item_summary_lines)
        else:
            item_summary = "No items owned."

        # Player stats
        self.stats_label.text = (
            f"Date: \n{player.game_time}\n\n"
            f"gold: ${player.gold:.2f}\n"
            f"Awareness: {player.dehydration_awareness}\n"
            f"hydration : {player.emergency_hydration}\n\n"
            f"items:\n{item_summary}\n"
        )

    def exit_game(self, instance):
        App.get_running_app().stop()

    def restart_game(self, instance):
        global player  # make sure we update the global reference

        print("DEBUG: Restarting game from GameOverScreen...")

        # Reset global game state
        player = reset_global_game_state()  # returns new Player object

        # Update ALL screens to use the new player and refresh their UI
        screens_to_update = [
            "user_status_screen",
            "item_market_screen",  # Fixed name - was "item_market"
            "ship_market_screen",  # Added ship market
            "sea_screen"  # Fixed name - was "SEA_screen"
        ]

        for screen_name in screens_to_update:
            try:
                screen = self.manager.get_screen(screen_name)
                if hasattr(screen, "player"):
                    screen.player = player
                    print(f"DEBUG: Updated player reference for {screen_name}")

                # Force refresh each screen's UI
                self.refresh_screen_ui(screen, screen_name)

            except Exception as e:
                print(f"DEBUG: Error updating {screen_name}: {e}")

        # Specifically refresh the user status screen items display
        try:
            user_status_screen = self.manager.get_screen("user_status_screen")
            user_status_screen.update_items_display()  # CRITICAL: This updates the scrollview
            user_status_screen.update_time_display()
            user_status_screen.update_durability_display()
            user_status_screen.stats_label.text = user_status_screen.get_stats_text()
            print("DEBUG: User status screen UI refreshed")
        except Exception as e:
            print(f"DEBUG: Error refreshing user status screen: {e}")

        # Clear any remaining widgets from game over screen
        self.clear_widgets()

        # Rebuild the game over screen layout for next time
        self.__init__(self.sm)

        # Go back to main menu (which should then go to user status screen)
        print("DEBUG: Navigating to main menu...")
        self.manager.current = "main_menu"

    def refresh_screen_ui(self, screen, screen_name):
        """Refresh the UI of specific screens after restart."""
        if screen_name == "user_status_screen":
            if hasattr(screen, 'update_items_display'):
                screen.update_items_display()
            if hasattr(screen, 'update_time_display'):
                screen.update_time_display()
            if hasattr(screen, 'update_durability_display'):
                screen.update_durability_display()
            if hasattr(screen, 'stats_label'):
                screen.stats_label.text = screen.get_stats_text()

        elif screen_name == "item_market_screen":
            if hasattr(screen, 'update_market_display'):
                screen.update_market_display()

        elif screen_name == "ship_market_screen":
            if hasattr(screen, 'populate_ships'):
                screen.populate_ships()
            if hasattr(screen, 'fleet_label'):
                screen.fleet_label.text = screen.get_fleet_info()

        elif screen_name == "sea_screen":
            # Reset SEA screen position and state
            if hasattr(screen, 'latitude'):
                screen.latitude = 0.0
            if hasattr(screen, 'longitude'):
                screen.longitude = 0.0
            if hasattr(screen, 'boat_x'):
                screen.boat_x = 100
            if hasattr(screen, 'boat_y'):
                screen.boat_y = 50
            if hasattr(screen, 'update_durability_display'):
                screen.update_durability_display()

class ItemMarket(Screen):
    def __init__(self, player, **kwargs):
        super().__init__(**kwargs)
        self.player = player
        self.items = items

        # FloatLayout for background layering
        self.layout = FloatLayout()

        # Background image
        bg = Image(source="Assets/item_market.png", allow_stretch=True, keep_ratio=False)
        self.layout.add_widget(bg)

        # Foreground UI
        ui_layout = BoxLayout(
            orientation='vertical',
            opacity=0.60,
            spacing=10,
            padding=20,
            size_hint=(0.9, 0.9),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )

        # Player gold label
        self.gold_label = Label(
            text=f"Gold: ${self.player.gold:,.2f}",
            font_size= 22,
            bold=True,
            size_hint=(1, None),
            height=45
        )
        ui_layout.add_widget(self.gold_label)

        # Ledger-style tabbed market
        self.tabs = TabbedPanel(
            do_default_tab=False,
            background_color=(0.1, 0.1, 0.1, 0.75),
            tab_height=45,
            tab_width=60,  # smaller tab width so they overlap more
            tab_pos='top_mid',
            strip_image='',  # remove bar background
            size_hint=(0.95, 0.3),
            pos_hint={'center_x': 0.5, 'center_y': 0.45}
        )

        with self.tabs.canvas.before:
            Color(0.1, 0.1, 0.1, 0.8)
            self.tabs.bg = RoundedRectangle(radius=[(10, 10), (10, 10), (0, 0), (0, 0)])

        ui_layout.add_widget(self.tabs)

        # Back button
        back_btn = Button(text="Back to Captain's Quarters", size_hint=(None, None), width=200, height=50)
        back_btn.bind(on_press=self.back_to_menu)
        ui_layout.add_widget(back_btn)

        self.layout.add_widget(ui_layout)
        self.add_widget(self.layout)

        # Now build the tabs dynamically
        self.populate_tabs()

    def populate_tabs(self):
        """Create one tab per item sector."""
        self.tabs.clear_tabs()
        self.tabs.tab_width = 120
        self.tabs.do_default_tab = False

        # Filter out "Treasure" sector and items without required keys
        valid_items = []
        for item in self.items:
            # Skip Treasure sector and check for required keys
            if item.get('sector') == "Treasure":
                continue

            # Check if item has required keys
            if 'sector' not in item:
                print(f"DEBUG: Item missing 'sector' key: {item}")
                continue
            if 'price' not in item:
                print(f"DEBUG: Item missing 'price' key: {item}")
                continue
            if 'name' not in item:
                print(f"DEBUG: Item missing 'name' key: {item}")
                continue

            valid_items.append(item)

        # Get unique sectors from valid items only
        sectors = sorted(set(item['sector'] for item in valid_items))
        print(f"DEBUG: Found sectors: {sectors}")
        print(f"DEBUG: Total valid items: {len(valid_items)}")

        for sector in sectors:
            # Create tab
            tab = TabbedPanelItem(
                text=sector,
                background_normal='',
                background_color=(0.1, 0.1, 0.1, 0.75),
                color=(1, 1, 1, 1)
            )

            # Create scroll view with proper settings
            scroll = ScrollView(
                size_hint=(1, 1),
                do_scroll_x=False,
                bar_width=10
            )

            # Create grid layout with proper height calculation
            grid = GridLayout(
                cols=2,
                spacing=15,
                padding=10,
                size_hint_y=None
            )

            # Add items for this sector with safe sorting
            sector_items = [i for i in valid_items if i['sector'] == sector]

            # Safe sorting with default values for missing keys
            sector_items = sorted(sector_items,
                                  key=lambda i: (i.get('price', 0), i.get('name', 'Unknown')))

            print(f"DEBUG: Sector '{sector}' has {len(sector_items)} items")

            for item in sector_items:
                # Get owned units with safe access
                owned_units = 0
                if hasattr(self.player, 'portfolio') and item['name'] in self.player.portfolio:
                    portfolio_data = self.player.portfolio[item['name']]
                    owned_units = portfolio_data[0] if isinstance(portfolio_data, tuple) else portfolio_data

                # Create button text with safe price access
                price = item.get('price', 0)
                item_name = item.get('name', 'Unknown Item')

                if owned_units > 0:
                    btn_text = f"{item_name}\n${price:,.2f}\nOwned: {owned_units}"
                else:
                    btn_text = f"{item_name}\n${price:,.2f}\nOwned: 0"

                # Create button
                btn = Button(
                    text=btn_text,
                    size_hint_y=None,
                    height=80,
                    background_normal='',
                    background_color=(0.8, 0.7, 0.5, 1),
                    color=(0.1, 0.1, 0, 1),
                    font_size='18sp',
                    bold=True,
                    halign='center',
                    valign='middle',
                    padding=(5, 5)
                )

                # Enable text wrapping
                btn.bind(
                    text_size=btn.setter('text_size'),
                    on_press=lambda instance, s=item: self.show_item_popup(s)
                )

                grid.add_widget(btn)

            # Calculate and set grid height AFTER adding all buttons
            row_height = 80 + 15  # button height + spacing
            num_rows = (len(sector_items) + 1) // 2  # +1 to round up
            grid.height = max(num_rows * row_height, 400)  # Minimum height

            scroll.add_widget(grid)
            tab.add_widget(scroll)
            self.tabs.add_widget(tab)

    def on_enter(self):
        """Refresh gold display when entering."""
        self.gold_label.text = f"Gold: ${self.player.gold:,.2f}"
        Clock.schedule_once(lambda dt: self.populate_tabs(), 0.1)

    def show_item_popup(self, item):
        """Show popup for buying/selling items."""
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # Show item image if available
        if "png" in item:
            image = Image(source=f"Assets/{item['png']}", size_hint_y=None, height=120)
            content.add_widget(image)

        # Owned units
        owned_units = 0
        if item['name'] in self.player.portfolio:
            portfolio_data = self.player.portfolio[item['name']]
            if isinstance(portfolio_data, tuple):
                owned_units = portfolio_data[0]
            else:
                owned_units = portfolio_data

        info = Label(
            text=f"[b]{item['name']}[/b]\nSector: {item['sector']}\nPrice: ${item['price']:.2f}\nOwned: {owned_units} units",
            markup=True, size_hint_y=None, height=100
        )
        content.add_widget(info)

        # Input for number of units
        units_input = TextInput(
            hint_text="Enter number of units",
            multiline=False,
            size_hint_y=None,
            height=40
        )
        content.add_widget(units_input)

        # Action buttons
        actions = BoxLayout(size_hint_y=None, height=50, spacing=10)

        # Create popup first so we can reference it in lambda
        popup = Popup(title="Item Actions", content=content, size_hint=(0.9, 0.9))

        for action in ["Buy", "Sell"]:
            btn = Button(text=action)
            btn.bind(on_press=lambda instance, a=action, i=item, s=units_input, p=popup:
            self.perform_item_action(a, i, s, p))
            actions.add_widget(btn)
        content.add_widget(actions)

        # Close button
        close_btn = Button(text="Close", size_hint_y=None, height=50)
        close_btn.bind(on_press=popup.dismiss)
        content.add_widget(close_btn)

        popup.open()

    def perform_item_action(self, action, item, units_input, popup):
        """Handle buying or selling items."""
        units_text = units_input.text.strip()

        if not units_text:
            self.show_error("Please enter number of units")
            return

        try:
            units = int(units_text)
        except ValueError:
            self.show_error("Please enter a valid number of units")
            return

        if units <= 0:
            self.show_error("Number of units must be positive")
            return

        # Perform Buy/Sell
        if action == "Buy":
            success, message = self.player.buy_item(item, units)
        elif action == "Sell":
            success, message = self.player.sell_item(item, units)
        else:
            self.show_error(f"Unknown action: {action}")
            return

        # Show result message
        popup_msg = Popup(
            title=f"{action} Result",
            content=Label(text=message),
            size_hint=(0.7, 0.3)
        )
        popup_msg.open()

        if success:
            # Update gold display immediately
            self.gold_label.text = f"Gold: ${self.player.gold:,.2f}"

            # DEBUG: Force immediate portfolio check
            print(f"DEBUG: After {action} - {item['name']} in portfolio: {item['name'] in self.player.portfolio}")
            if item['name'] in self.player.portfolio:
                portfolio_data = self.player.portfolio[item['name']]
                owned = portfolio_data[0] if isinstance(portfolio_data, tuple) else portfolio_data
                print(f"DEBUG: {item['name']} owned units: {owned}")

            # Close the action popup first
            popup.dismiss()

            # FORCE UI refresh - completely rebuild the tabs
            def force_refresh(dt):
                print("DEBUG: Force refreshing market display...")
                # Clear and completely rebuild
                self.tabs.clear_tabs()
                self.populate_tabs()

                # Also force refresh the layout
                self.layout.do_layout()

            # Use Clock to ensure UI updates
            Clock.schedule_once(force_refresh, 0.1)

            # Update UserStatusScreen
            user_screen = self.manager.get_screen("user_status_screen")
            if user_screen:
                user_screen.stats_label.text = user_screen.get_stats_text()
                if hasattr(user_screen, 'update_items_display'):
                    user_screen.update_items_display()

        else:
            # Show error but keep popup open
            print(f"{action} failed: {message}")

    def show_error(self, message):
        """Show error popup."""
        popup = Popup(
            title="Error",
            content=Label(text=message),
            size_hint=(0.6, 0.3)
        )
        popup.open()

    def back_to_menu(self, instance):
        """Return to user status screen."""
        self.manager.current = "user_status_screen"

class ExcursionSelect(Screen):
    def __init__(self, player, **kwargs):
        super().__init__(**kwargs)
        self.player = player
        self.layout = FloatLayout()

        # Background image
        bg = Image(source="Assets/harbor.png", allow_stretch=True, keep_ratio=False)
        self.layout.add_widget(bg)

        # Foreground UI layout
        ui_layout = BoxLayout(
            orientation='vertical', spacing=20, padding=20,
            opacity=0.7,
            size_hint=(0.9, 0.9), pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )

        # Title
        title = Label(text="Excursion Selection", font_size=30, size_hint=(1, None), height=50)
        ui_layout.add_widget(title)

        # Scrollable excursion list
        scroll = ScrollView(size_hint=(1, 1), bar_width=20, bar_color=(0.3, 1, 0.3, 1))
        self.excursion_grid = GridLayout(cols=1, size_hint_y=None, spacing=10)
        self.excursion_grid.bind(minimum_height=self.excursion_grid.setter('height'))
        scroll.add_widget(self.excursion_grid)
        ui_layout.add_widget(scroll)

        # Back button
        back_btn = Button(text="Back to Captain's Quarters", size_hint=(None, None), width=200, height=50)
        back_btn.bind(on_press=self.back_to_items)
        ui_layout.add_widget(back_btn)

        self.layout.add_widget(ui_layout)
        self.add_widget(self.layout)

        # Populate excursions
        self.populate_excursions()

    def populate_excursions(self):
        self.excursion_grid.clear_widgets()
        for name, data in excursions.items():
            # Calculate dehydration cost range
            min_dehyd, max_dehyd = data.get('dehydration_cost', (5, 15))

            btn_text = (
                f"{name}\n"
                f"Reward: ${data['reward']:,} | "
                f"Risk: {data['success_rate']}% | "
                f"Dehydration: {min_dehyd}-{max_dehyd}"
            )

            btn = Button(
                text=btn_text,
                size_hint_y=None,
                height=80,  # Taller to fit more info
                halign='left'
            )
            btn.bind(on_press=lambda instance, n=name, d=data: self.start_excursion(n, d))
            self.excursion_grid.add_widget(btn)

    def start_excursion(self, excursion_name, excursion_data):
        sector = excursion_data['sector']

        # Calculate random dehydration cost
        min_dehyd, max_dehyd = excursion_data.get('dehydration_cost', (5, 15))
        dehydration_increase = random.randint(min_dehyd, max_dehyd)

        # Apply dehydration
        self.player.dehydration_awareness += dehydration_increase

        # Check for success
        base_rate = excursion_data["success_rate"]
        if self.player.speed > 10:
            base_rate += 5
        if self.player.dehydration_awareness > 50:
            base_rate -= 15
        if sector == "Combat" and any("sword" in i["name"].lower() for i in items):
            base_rate += 10
        if sector == "Combat" and any("dagger" in i["name"].lower() for i in items):
            base_rate += 5
        if sector == "Combat" and any("rapier" in i["name"].lower() for i in items):
            base_rate += 12
        if sector == "Combat" and any("cutlass" in i["name"].lower() for i in items):
            base_rate += 13
        if sector == "Combat" and any("rifle" in i["name"].lower() for i in items):
            base_rate += 20
        if sector == "Combat" and any("pistol" in i["name"].lower() for i in items):
            base_rate += 15
        if sector == "Combat" and any("halberd" in i["name"].lower() for i in items):
            base_rate += 18
        if sector == "Combat" and any("axe" in i["name"].lower() for i in items):
            base_rate += 19
        if sector == "Combat" and any("canon" in i["name"].lower() for i in items):
            base_rate += 30
        if sector == "Combat" and any("blunderbuss" in i["name"].lower() for i in items):
            base_rate += 22


        success = random.randint(1, 100) <= min(95, max(5, base_rate))

        if success:
            # SUCCESS: Gain rewards
            base_reward = excursion_data["reward"]

            # Apply risk-based reward scaling
            risk_factor = (100 - excursion_data["success_rate"]) / 100
            reward = int(base_reward * (1 + (risk_factor * random.uniform(0.5, 1.5))))

            self.player.gold += reward

            # Apply sector boost
            for item in items:
                if item['sector'] == sector:
                    change = random.uniform(item['effect'][0], item['effect'][1]) + item['price'] * 0.10
                    item['price'] += change

            # Apply sector bonuses
            if sector == "Navigation":
                self.player.nav_bonus = getattr(self.player, "nav_bonus", 0) + 0.05
            elif sector == "Combat":
                self.player.combat_bonus = getattr(self.player, "combat_bonus", 0) + 0.05

            # Handle special effects
            special_message = ""
            if "special_effect" in excursion_data:
                special_message = f"\nSpecial: {excursion_data['special_effect']}"

                # Apply specific special effects
                if "Fountain of Youth" in excursion_name:
                    self.player.dehydration_awareness = 0  # Reset dehydration
                    special_message = "\nSpecial: Dehydration completely reset!"
                elif "Navigation bonus" in excursion_data.get('special_effect', ''):
                    # Apply temporary navigation bonus
                    special_message = "\nSpecial: +20% navigation speed next voyage!"

            # High-risk bonus for low success rate excursions
            if excursion_data["success_rate"] <= 25:
                fate_roll = random.randint(1, 100)
                if fate_roll <= 15:
                    bonus_reward = excursion_data["reward"] * 2
                    self.player.gold += bonus_reward
                    special_message += f"\nSpecial: Against all odds, you returned triumphant with double loot! +${bonus_reward:,}"

            result_message = (
                f"EXCURSION SUCCESS: {excursion_name}\n"
                f"Description: {excursion_data.get('description', '')}\n"
                f"Gold Gained: ${reward:,}\n"
                f"Sector Boosted: {sector}\n"
                f"Dehydration Increase: +{dehydration_increase}"
                f"{special_message}"
            )

        else:
            # FAILURE: Handle different types of losses
            loss_type = random.choice(["gold", "item", "ship"])
            consequence = ""

            if loss_type == "gold" and self.player.gold > 0:
                loss = int(self.player.gold * random.uniform(0.05, 0.25))
                self.player.gold -= loss
                consequence = f"You lost ${loss:,} in damages!"

            elif loss_type == "item" and self.player.portfolio:
                # Choose a random item from player's portfolio
                if self.player.portfolio:
                    item_name = random.choice(list(self.player.portfolio.keys()))
                    units, total_cost = self.player.portfolio[item_name]
                    if units > 0:
                        # Remove one unit of the item
                        if units == 1:
                            del self.player.portfolio[item_name]
                        else:
                            self.player.portfolio[item_name] = (units - 1, total_cost - (total_cost / units))
                        consequence = f"You lost 1 unit of {item_name}!"
                    else:
                        consequence = "You narrowly escaped with your life!"
                else:
                    consequence = "You narrowly escaped with your life!"

            else:
                # Ship damage - use durability system instead of ship_durability
                damage = random.randint(10, 25)
                self.player.durability_current = max(0, self.player.durability_current - damage)
                consequence = f"Your ship took {damage} damage! Durability: {self.player.durability_current}/{self.player.durability_max}"

            result_message = (
                f"EXCURSION FAILED: {excursion_name}\n"
                f"Consequence: {consequence}\n"
                f"Description: {excursion_data.get('description', '')}\n"
                f"The mission was unsuccessful!\n"
                f"Dehydration Increase: +{dehydration_increase}\n"
                f"Better luck next time, captain!"
            )

        # Update game state
        user_screen = self.manager.get_screen("user_status_screen")
        user_screen.advance_time(3)
        user_screen.stats_label.text = user_screen.get_fleet_stats_text()
        user_screen.update_items_display()
        user_screen.update_durability_display()

        # Show result popup - pass success status and reward amount
        if success:
            self.show_popup(result_message, success, reward)
        else:
            self.show_popup(result_message, success, 0)  # 0 reward for failures

    def discover_secret_location(self, location_name):
        if location_name in secret_locations:
            loc = secret_locations[location_name]
            if location_name not in excursions:
                excursions[location_name] = {
                    "success_rate": 40,
                    "reward": random.randint(50000, 150000),
                    "sector": random.choice(["Navigation", "Combat", "Luxury"]),
                    "dehydration_cost": (5, 15),
                    "description": loc["description"] + " (Special discovery reward!)",
                    "special_effect": "Unlocked by exploration"
                }
            self.populate_excursions()

    def show_popup(self, message, was_successful, reward_gained=0):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)

        label = Label(
            text=message,
            halign='center',
            valign='top',
            text_size=(500, None)
        )
        content.add_widget(label)

        # Add mini-game chance for successful excursions
        if was_successful and random.random() < 0.35:  # 35% chance
            mini_btn = Button(
                text="Play Mini-Game for Bonus!",
                size_hint_y=None,
                height=50
            )
            mini_btn.bind(on_press=lambda x: self.launch_mini_game())
            content.add_widget(mini_btn)

        close_btn = Button(text="Continue", size_hint_y=None, height=50)
        content.add_widget(close_btn)

        popup = Popup(
            title="Excursion Results",
            content=content,
            size_hint=(0.8, 0.7)
        )

        # Initialize excursion stats if they don't exist
        if not hasattr(self.player, "excursion_stats"):
            self.player.excursion_stats = {"success": 0, "fail": 0, "total_gold": 0}

        # Update stats using the parameters passed to this method
        if was_successful:
            self.player.excursion_stats["success"] += 1
            self.player.excursion_stats["total_gold"] += reward_gained
        else:
            self.player.excursion_stats["fail"] += 1

        close_btn.bind(on_press=popup.dismiss)
        popup.open()

    def launch_mini_game(self):
        """Launch a random mini-game after successful excursion."""
        from minigames import (
            CanonBlastMiniGame, PodiumMiniGame, CanonLoaderMiniGame, SeaBattleMiniGame, SabotageMiniGame,
            PearlDiverMiniGame, DiceRollingMiniGame
        )

        games = [
            ("Canon Blast", "canon", CanonBlastMiniGame),
            ("Podium", "podium", PodiumMiniGame),
            ("Canon Loader", "canon_loader", CanonLoaderMiniGame),
            ("Sea Battle", "sea_battle", SeaBattleMiniGame),
            ("Sabotage", "sabotage", SabotageMiniGame),
            ("Pearl Diver", "pearl_diver", PearlDiverMiniGame),
            ("Dice Rolling", "dice_rolling", DiceRollingMiniGame)
        ]

        title, name, cls = random.choice(games)

        # Register if not already in ScreenManager
        if not self.manager.has_screen(name):
            self.manager.add_widget(cls(
                player=self.player,
                user_status_screen=self.manager.get_screen("user_status_screen"),
                name=name
            ))

        # Switch to mini-game
        self.manager.current = name

    def back_to_items(self, instance):
        self.manager.current = "user_status_screen"

class MiniGameMenu(Screen):
    def __init__(self, player, user_status_screen, **kwargs):
        super().__init__(**kwargs)
        self.player = player
        self.user_status_screen = user_status_screen
        self.btn_layout = None  # we'll create later

        # Base layout and UI...
        base_layout = FloatLayout()
        self.add_widget(base_layout)

        base_layout.add_widget(Image(source="Assets/ancient_map.png", allow_stretch=True, keep_ratio=False))
        title = Label(
            text="BarelySober 1592 MiniGames",
            font_size=45,
            size_hint=(None, None),
            size=(Window.width, 50),
            pos_hint={'center_x': 0.5, 'top': 0.95},
            bold=True
        )
        base_layout.add_widget(title)

        # Scrollable button area
        scroll = ScrollView(size_hint=(0.4, 0.4), bar_width=40, bar_color=(0.3, 1, 0.3, 1), pos_hint={'x': 0.58, 'y': 0.1})
        self.btn_layout = GridLayout(cols=1, spacing=10, opacity=0.8, size_hint_y=None)
        self.btn_layout.bind(minimum_height=self.btn_layout.setter('height'))
        scroll.add_widget(self.btn_layout)
        base_layout.add_widget(scroll)

        # Back button at the bottom
        back_btn = Button(text="Back to Office", size_hint=(1, None), height=60)
        back_btn.bind(on_press=lambda inst: setattr(self.manager, 'current', 'user_status_screen'))
        self.btn_layout.add_widget(back_btn)

    def on_enter(self, *args):
        App.get_running_app().entry_path = "mini"
        if not hasattr(self, "_games_registered"):
            self.register_games()
            self._games_registered = True

    def register_games(self):

        games = [
            ("Canon Blasts", "canon", CanonBlastMiniGame),
            ("Podium", "podium", PodiumMiniGame),
            ("Canon Loader", "canon_loader", CanonLoaderMiniGame),
            ("SEA Battle", "sea_battle", SeaBattleMiniGame),
            ("Sabotage", "sabotage", SabotageMiniGame),
            ("Pearl Diver", "pearl_diver", PearlDiverMiniGame),
            ("Dice Rolling", "dice_rolling", DiceRollingMiniGame)
        ]

        for title, name, cls in games:
            btn = Button(text=title, bold=True, size_hint=(1, None), height=60)
            btn.bind(on_press=lambda inst, n=name: setattr(self.manager, 'current', n))
            self.btn_layout.add_widget(btn)

            if not self.manager.has_screen(name):
                self.manager.add_widget(cls(player=self.player, user_status_screen=self.user_status_screen, name=name))

sm = ScreenManager()
# 1. User Status
user_status_screen = UserStatusScreen(player, name="user_status_screen")
sm.add_widget(user_status_screen)

# 2. Game Over Screen
game_over_screen = GameOverScreen(sm, name="game_over")
sm.add_widget(game_over_screen)

# 3. Main Menu
sm.add_widget(MainMenu(name="main_menu"))

# 4. MiniGameMenu (pass the player and user_status_screen)
game_menu = MiniGameMenu(player=player, user_status_screen=user_status_screen, name="game_menu")
sm.add_widget(game_menu)

game_menu.register_games()

# 5. Other screens
sm.add_widget(ItemMarket(player=player, name="item_market"))
sm.add_widget(ExcursionSelect(player=player, name="excursion_select"))
sm.add_widget(SEAScreen(player=player, name="SEA_screen"))
sm.add_widget(ShipMarketScreen(player, name="ship_market"))
sm.current = "main_menu"

class BarelySober1592App(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.entry_path = None  # Initialize here

    def build(self):
        self.entry_path = None  # flag: "start", "load", "mini"
        return sm

if __name__ == "__main__":
    print("🧹 Reinitializing databases...")

    for path in [ITEM_DB_PATH, SHIP_DB_PATH]:
        if os.path.exists(path):
            os.remove(path)
            print(f"Deleted old {path}")

    init_databases()    # create table if it doesn't exist
    BarelySober1592App().run()
