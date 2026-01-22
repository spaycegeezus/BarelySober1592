# mini_games.py
from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, PushMatrix, InstructionGroup, PopMatrix, Scale, Translate, Line, Rotate
import random
from kivy.properties import ObjectProperty
from database import excursions, secret_locations, populate_items
import math
import colorsys
import sqlite3
from kivy.core.image import Image as CoreImage
from logic import Player
from assets_loader import preload_assets, ASSETS
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
import datetime as dt
conn = sqlite3.connect("game_data/item_market.db")
cursor = conn.cursor()

# --- Player ---
player = Player()
player.dehydration_awareness = 0
WIDTH, HEIGHT = Window.size

class GameMenu(Screen):
    def __init__(self, player, **kwargs):
        super().__init__(**kwargs)
        self.player = player

        # Base layout for menu
        base_layout = FloatLayout()
        self.add_widget(base_layout)

        # Background ancient_map
        base_layout.add_widget(Image(
            source="Assets/ancient_map.png",
            allow_stretch=True,
            keep_ratio=False
        ))

        # Title
        title = Label(
            text="Propagandist 33 MiniGames",
            font_size=45,
            size_hint=(None, None),
            size=(Window.width, 50),
            pos_hint={'center_x': 0.5, 'top': 0.95},
            bold=True
        )
        base_layout.add_widget(title)

        # Scrollable button area
        scroll = ScrollView(
            size_hint=(0.5, 0.4),
            bar_width=20,
            bar_color=(0.3, 1, 0.3, 1),
            pos_hint={'x': 0.25, 'y': 0.1}
        )

        btn_layout = GridLayout(
            cols=1,
            spacing=10,
            opacity=0.7,
            size_hint_y=None
        )
        btn_layout.bind(minimum_height=btn_layout.setter('height'))

        buttons = {
            "Canon Blasts": "canon",
            "Bullet Podium": "podium",
            "Sea Battle": "sea_battle",
            "Pearl Diver": "pearl_diver",
            "Canon Loader": "canon_loader",
            "Bail Water": "sabotage",
            "Dice Rolling": "Dice_rolling",
            "Back to the Office": "user_status_screen",  # Changed from "main"
        }

        for text, screen_name in buttons.items():
            btn = Button(text=text, size_hint=(1, None), height=60)
            btn.bind(on_press=lambda inst, sn=screen_name: self.switch_screen(sn))
            btn_layout.add_widget(btn)

        scroll.add_widget(btn_layout)
        base_layout.add_widget(scroll)

    def switch_screen(self, screen_name):
        # Set entry path when navigating to mini-games from the menu
        if screen_name not in ["user_status_screen", "main_menu"]:
            App.get_running_app().entry_path = "mini"
        self.manager.current = screen_name

class BaseMiniGame(Screen):
    user_status_screen = ObjectProperty(None)

    def __init__(self, player, difficulty=1, **kwargs):
        super().__init__(**kwargs)
        self.player = player
        self.difficulty = difficulty
        self.active = False
        self.event = None

        # Root layout (fills screen)
        self.base_layout = FloatLayout()
        self.add_widget(self.base_layout)

        # Placeholder for game-specific widgets
        self.game_area = FloatLayout()
        self.base_layout.add_widget(self.game_area)

        # Back button pinned to bottom-left
        self.back_btn = Button(
            text="Back",
            size_hint=(0.15, 0.1),
            pos_hint={"x": 0, "y": 0}
        )
        self.back_btn.bind(on_press=self.go_back)
        self.base_layout.add_widget(self.back_btn)

    def go_back(self, instance):
        if self.manager:
            # Check where we came from to decide where to return
            entry = App.get_running_app().entry_path
            if entry == "mini":
                self.manager.current = "game_menu"
            else:
                self.manager.current = "user_status_screen"
        self.game_area.clear_widgets()

    def on_enter(self, *args):
        self.active = True
        if self.user_status_screen:
            self.user_status_screen.update_time_display()

    def reset_game_state(self):
        self.active = False
        if self.event:
            Clock.unschedule(self.event)
            self.event = None
        self.game_area.clear_widgets()

    def on_leave(self, *args):
        self.active = False
        if self.event:
            Clock.unschedule(self.event)
            self.reset_game_state()
            self.event = None

    def excursion_success(self, message="excursion Success!", gold_reward=0):
        rare_bonus = ""
        if random.random() < 0.05:  # 5% rare chance
            rare_bonus = (
                "\nHYDRATION BONUS! \nThe Gods of the sea bless you with an island flowing with fresh water, "
                "\n\n Your sobriety helps with your study of the stars.")
            self.player.dehydration_awareness = max(0, self.player.dehydration_awareness - 20)
            self.player.gold = max(self.player.gold + 100000, 0)
            self.player.gold = max(self.player.gold + 10000, 0)

        # Add the custom gold reward if provided
        if gold_reward > 0:
            self.player.gold += gold_reward
            message += f"\nGold Earned: ${gold_reward:,}"

        final_message = message + rare_bonus

        if not self.active:
            return
        self.active = False
        if self.event:
            Clock.unschedule(self.event)

        # Create popup
        popup = Popup(
            title="Success",
            content=Label(text=final_message, halign="center"),
            size_hint=(0.6, 0.4)
        )
        popup.open()

        def on_popup_dismiss(instance):
            app = App.get_running_app()
            if app.root:
                entry = getattr(app, "entry_path", None)
                if entry == "mini":
                    app.root.current = "game_menu"
                else:
                    app.root.current = "user_status_screen"

    def excursion_fail(self, message="excursion Failed!"):
        if not self.active:
            return
        self.active = False
        if self.event:
            Clock.unschedule(self.event)

        # Create popup
        popup = Popup(
            title="Failed",
            content=Label(text=message),
            size_hint=(0.6, 0.4)
        )

        def on_popup_dismiss(instance):
            # Return to appropriate screen based on entry path
            if self.manager:
                entry = App.get_running_app().entry_path
                if entry == "mini":
                    self.manager.current = "game_menu"
                else:
                    self.manager.current = "user_status_screen"

        popup.bind(on_dismiss=on_popup_dismiss)
        popup.open()


class CanonBlastMiniGame(BaseMiniGame):
    user_status_screen = ObjectProperty(None)

    def __init__(self, player, difficulty=1, **kwargs):
        super().__init__(player, difficulty, **kwargs)
        self.difficulty = difficulty
        # Don't initialize game state here - wait for on_enter
        self.lasers_remaining = 0
        self.planes = []
        self.buildings = []
        self.active_lasers = []
        self.total_planes_to_spawn = 10
        self.planes_spawned = 0
        self.spawn_interval = None
        self.bg_img = None
        self.satellite = None
        self.fire_btn = None

    def build_game(self):
        # Background
        self.bg_img = Image(source="Assets/space.png", allow_stretch=True, keep_ratio=False)
        self.game_area.add_widget(self.bg_img)
        self.bind(size=self.update_bg, pos=self.update_bg)

        # Satellite (static at top center)
        self.satellite = Image(source="Assets/satellite.png", size_hint=(None, None),
                               size=(150, 100))
        self.game_area.add_widget(self.satellite)
        self.bind(size=self.update_satellite)

        # Buildings
        self.create_buildings()

        # Fire button
        self.fire_btn = Button(text=f"Fire Laser ({self.lasers_remaining})",
                               size_hint=(None, None),
                               width=200, height=50)
        self.fire_btn.bind(on_press=self.fire_laser)
        self.game_area.add_widget(self.fire_btn)

        # Update positions
        self.update_satellite()
        self.update_bg()
        self.update_fire_btn()

    def update_fire_btn(self):
        """Update fire button position"""
        if self.fire_btn:
            self.fire_btn.pos = (self.width / 2 - 100, 20)

    def start_game(self, dt=None):
        """Start or restart the game"""
        # Reset game state
        self.lasers_remaining = max(5, 10 + (self.difficulty - 1) * 2)  # Fixed calculation
        self.planes_spawned = 0
        self.planes.clear()
        self.active_lasers.clear()

        # Build game elements if not already built
        if not self.bg_img:
            self.build_game()
        else:
            # Update fire button text
            self.fire_btn.text = f"Fire Laser ({self.lasers_remaining})"

        # Start spawn interval
        if self.spawn_interval:
            Clock.unschedule(self.spawn_interval)
        self.spawn_interval = Clock.schedule_interval(self.spawn_plane_periodic, 1.0)

        # Start update loop
        if self.event:
            Clock.unschedule(self.event)
        self.event = Clock.schedule_interval(self.update_game, 1 / 30.0)

        # Spawn initial plane
        Clock.schedule_once(lambda dt: self.spawn_plane(), 0.5)

    def update_satellite(self, *args):
        if self.satellite:
            self.satellite.pos = (self.width / 2 - 75, self.height - 100)

    def update_bg(self, *args):
        if self.bg_img:
            self.bg_img.size = self.size
            self.bg_img.pos = self.pos

    def create_buildings(self):
        """Create building elements"""
        building_width = 250
        spacing = 10
        num_buildings = 10

        for i in range(num_buildings):
            x_pos = i * (building_width + spacing)
            building = Image(
                source="Assets/buildings.png",
                size_hint=(None, None),
                size=(building_width, 150),
                pos=(x_pos, 0)
            )
            self.buildings.append(building)
            self.game_area.add_widget(building)

    def spawn_plane(self):
        """Spawn a new plane"""
        if self.planes_spawned >= self.total_planes_to_spawn:
            return

        # Random vertical position (avoid top and bottom edges)
        min_y = 150
        max_y = self.height - 200
        if max_y < min_y:
            max_y = min_y + 100  # Ensure we have some range

        plane_y = random.randint(min_y, max_y)

        # Randomly decide spawn side: True = left, False = right
        spawn_left = random.choice([True, False])

        plane_width = 70
        plane_height = 40

        if spawn_left:
            plane = Image(
                source="Assets/plane_right.png",
                size_hint=(None, None),
                size=(plane_width, plane_height),
                pos=(0, plane_y)
            )
            plane.speed = 2 + self.difficulty
        else:
            plane = Image(
                source="Assets/plane_left.png",
                size_hint=(None, None),
                size=(plane_width, plane_height),
                pos=(self.width - plane_width, plane_y)
            )
            plane.speed = -(2 + self.difficulty)

        self.game_area.add_widget(plane)
        self.planes.append(plane)
        self.planes_spawned += 1

    def spawn_plane_periodic(self, dt):
        """Periodically spawn planes"""
        if self.active and len(self.planes) < self.difficulty + 2:  # Allow a few more planes
            self.spawn_plane()

    def fire_laser(self, instance):
        """Fire laser at a plane"""
        if self.lasers_remaining <= 0 or not self.active or not self.planes:
            return

        self.lasers_remaining -= 1
        self.fire_btn.text = f"Fire Laser ({self.lasers_remaining})"

        # Target the first plane
        target_plane = self.planes[0]
        self.active_lasers.append({'target': target_plane, 'time': 0.2})

    def update_game(self, dt):
        """Main game update loop"""
        if not self.active:
            return

        # Update plane positions
        for plane in self.planes[:]:
            plane.x += plane.speed

            # Add slight vertical movement
            plane.y += random.choice([-1, 0, 1])

            # Keep plane within vertical bounds
            plane.y = max(50, min(plane.y, self.height - 100))

            # Update plane image based on direction
            if plane.speed > 0:
                plane.source = "Assets/plane_right.png"
            else:
                plane.source = "Assets/plane_left.png"

            # Check if plane escaped
            if (plane.speed > 0 and plane.x > self.width) or (plane.speed < 0 and plane.x < -plane.width):
                self.planes.remove(plane)
                if plane.parent:
                    plane.parent.remove_widget(plane)
                continue

        # Process lasers
        self.canvas.after.clear()
        for laser in self.active_lasers[:]:
            laser['time'] -= dt
            target = laser['target']

            if laser['time'] <= 0 or target not in self.planes:
                self.active_lasers.remove(laser)
                continue

            # Draw laser line
            with self.canvas.after:
                Color(1, 0, 0, 0.7)
                Line(points=[
                    self.satellite.center_x, self.satellite.center_y,
                    target.center_x, target.center_y
                ], width=2)

            # Check collision - remove plane and laser
            if target in self.planes:
                self.planes.remove(target)
                if target.parent:
                    target.parent.remove_widget(target)

                # Add explosion effect
                explosion = Image(
                    source="Assets/explosion.png",
                    size_hint=(None, None),
                    size=(70, 60),
                    pos=(target.x - 10, target.y - 10)
                )
                self.game_area.add_widget(explosion)
                Clock.schedule_once(lambda dt: self.remove_explosion(explosion), 0.5)

            self.active_lasers.remove(laser)

        # Check win/lose conditions
        if self.planes_spawned >= self.total_planes_to_spawn and not self.planes:
            self.excursion_success("All planes destroyed! You win!")
            return

        if self.lasers_remaining <= 0 and self.planes:
            self.excursion_fail("Out of lasers! You lose!")
            return

    def remove_explosion(self, explosion):
        """Remove explosion effect"""
        if explosion.parent:
            explosion.parent.remove_widget(explosion)

    def on_enter(self, *args):
        """Called when screen is entered"""
        super().on_enter(*args)
        self.start_game()

    def on_leave(self, *args):
        """Called when screen is left"""
        if self.spawn_interval:
            Clock.unschedule(self.spawn_interval)
            self.spawn_interval = None
        super().on_leave(*args)

    def reset_game_state(self):
        super().reset_game_state()
        if self.spawn_interval:
            Clock.unschedule(self.spawn_interval)
            self.spawn_interval = None

        # Reset counters
        self.planes_spawned = 0
        self.lasers_remaining = 0

        # Clear references so build_game() runs again
        self.bg_img = None
        self.satellite = None
        self.fire_btn = None
        self.buildings = []


class PodiumMiniGame(BaseMiniGame):
    user_status_screen = ObjectProperty(None)
    def __init__(self, player, difficulty=1, **kwargs):
        super().__init__(player, difficulty, **kwargs)

        # Background
        with self.canvas.before:
            self.bind(size=self.update_game_area, pos=self.update_game_area)
        self.active = True
        self.projectiles = []
        with self.canvas:
            self.line = Line(points=[0, 0, 0, 0], width=2)

        # Podium
        self.podium = Image( source="Assets/ship_market.png", size_hint=(0.75, 0.75), allow_stretch=True, keep_ratio=True, size=Window.size)
        self.game_area.add_widget(self.podium)

        # canon
        self.guy = Image(
            source="Assets/rear_view_canon.png",
            size_hint=(None, None),
            size=(100, 80),  # positive values only!
        )
        self.guy.speed = 2 + difficulty
        self.game_area.add_widget(self.guy)

        # Target
        self.target = Image(source="Assets/boat.png", size_hint=(None, None), size=(100, 100))
        self.game_area.add_widget(self.target)

        # Fire button
        self.fire_btn = Button(text="Fire", size_hint=(None, None), width=150, height=50,
                               pos=(self.width - -500, 50))
        self.fire_btn.bind(on_press=self.fire)
        self.game_area.add_widget(self.fire_btn)

        # Movement update
        self.event = Clock.schedule_interval(self.update_guy, 1 / 60)
        # Key control
        Window.bind(on_key_down=self.on_key_down)

        # Make sure podium + guy are placed initially
        self.projectile_event = Clock.schedule_interval(self.update_projectiles, 1 / 60)
        Clock.schedule_once(self.update_podium, 0)

    def start_game(self, dt=None):
        # Optional: start the first increment immediately
        self.update_podium(None)

    def update_game_area(self, *args):
        self.game_area.size = self.size
        self.game_area.pos = self.pos

    def on_key_down(self, window, key, scancode, codepoint, modifier):
        if not self.active:
            return
        # Example: move left/right
        if key == 276:  # left arrow
            self.guy.x -= 10
        elif key == 275:  # right arrow
            self.guy.x += 10

    def update_podium(self, *args):
        podium_width = self.width * (2 / 3)
        podium_height = 120
        podium_y = 100

        # Resize & center podium
        self.podium.size = (podium_width, podium_height)
        self.podium.pos = (self.width / 2 - podium_width / 2, podium_y)

        # Wizard overlaps top of podium by 20px
        self.guy.size = (100, 80)  # keep consistent
        self.guy.x = self.podium.center_x - self.guy.width / 8
        self.guy.y = self.podium.top - 220

    def update_guy(self, dt):
        if not self.active:
            return

        x, y = self.guy.pos
        x += self.guy.speed

        # Keep within podium bounds
        if x <= self.podium.x:
            x = self.podium.x
            self.guy.speed *= -1
        elif x + self.guy.width >= self.podium.x + self.podium.width:
            x = self.podium.x + self.podium.width - self.guy.width
            self.guy.speed *= -1

        # Always keep guy aligned with bottom of podium
        self.guy.pos = (x, self.podium.y)

        # Update trajectory line
        self.line.points = [self.guy.center_x, self.guy.top, self.guy.center_x, self.height * 0.9]

        # update trajectory line — wider than just podium-to-target
        target_zone_top = self.target.y + self.target.height
        line_end_y = min(self.height * 0.9, target_zone_top + 200)  # extend above target

    def reset_target(self):
        start_x = int(self.podium.x)
        end_x = int(self.podium.x + self.podium.width + 50 - self.target.width - 100)

        self.target.x = random.randint(start_x, end_x)
        # spawn lower than max line
        self.target.y = int(self.podium.top + 50)
        self.target.opacity = 1

    def on_enter(self, *args):
        # Set game_area to fill screen
        self.reset_game_state()
        self.update_game_area()
        # Place podium & guy correctly
        self.update_podium()
        # Place target
        self.reset_target()
        # Start movement loop
        self.active = True
        self.event = Clock.schedule_interval(self.update_guy, 1 / 60)

    def reset_game_state(self):
        # Stop current movement/projectiles
        self.active = False
        Clock.unschedule(self.update_guy)
        Clock.unschedule(self.update_projectiles)

        # Clear projectiles
        for projectile in self.projectiles[:]:
            if projectile.parent:
                self.game_area.remove_widget(projectile)
            self.projectiles.remove(projectile)

        # Reset wizard position & speed
        self.guy.speed = 2 + self.difficulty
        self.guy.x = self.podium.center_x - self.guy.width / 8
        self.guy.y = self.podium.top - 220

        # Reset target
        self.reset_target()

        # Reset line
        self.line.points = [self.guy.center_x, self.guy.top, self.guy.center_x, self.height * 0.9]

        # Reactivate loops
        self.active = True
        self.event = Clock.schedule_interval(self.update_guy, 1 / 60)
        self.projectile_event = Clock.schedule_interval(self.update_projectiles, 1 / 60)

    def fire(self, instance):
        if not self.active:
            return

        # Create projectile
        projectile = Image(
            source="Assets/projectile.png",
            size_hint=(None, None),
            size=(20, 40),
            pos=(self.guy.center_x - 10, self.guy.top)
        )
        self.game_area.add_widget(projectile)
        self.projectiles.append(projectile)

    def update_projectiles(self, dt):
        if not self.active:
            return

        for projectile in self.projectiles[:]:
            projectile.y += 10  # projectile speed

            # Collision check with target
            if self.target.opacity == 1 and projectile.collide_widget(self.target):
                # excursion success
                self.excursion_success("Target hit!")

                # Show hit image
                hit_effect = Image(
                    source="Assets/target_hit.png",
                    size_hint=(None, None),
                    size=(self.target.width, self.target.height),
                    pos=self.target.pos
                )
                self.game_area.add_widget(hit_effect)

                # Fade out effect after short delay
                Clock.schedule_once(lambda dt: self.game_area.remove_widget(hit_effect), 0.3)

                # Remove target & projectile
                self.target.opacity = 0
                if projectile.parent:
                    self.game_area.remove_widget(projectile)
                self.projectiles.remove(projectile)

            # If projectile goes off screen
            elif projectile.y > self.height:
                if projectile.parent:
                    self.game_area.remove_widget(projectile)
                self.projectiles.remove(projectile)
                self.excursion_fail("Missed!")

class SabotageMiniGame(BaseMiniGame):
    user_status_screen = ObjectProperty(None)
    def __init__(self, player, difficulty=1, **kwargs):
        super().__init__(player, difficulty, **kwargs)
        self.player = player
        self.difficulty = difficulty
        self.active = True
        sm = ScreenManager()
        # Progress tracking
        self.progress = 0
        self.max_progress = 20 - (difficulty - 1) * 2  # Lower number = easier at low difficulty

        self.bg_img = Image(source="Assets/sinking_ship.png", allow_stretch=True, keep_ratio=False,
                            size=self.size, pos=self.pos)
        self.game_area.add_widget(self.bg_img)
        self.bind(size=self.update_bg, pos=self.update_bg)

        # Layout
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        self.game_area.add_widget(self.layout)

        # Instructions
        self.label = Label(text="Bail the ship before it sinks!!! Click the button rapidly to succeed.", font_size=20)
        self.layout.add_widget(self.label)

        # Progress display
        self.progress_label = Label(text=f"Progress: {self.progress}/{self.max_progress}", font_size=18)
        self.layout.add_widget(self.progress_label)

        # Click button
        btn_w, btn_h = 250, 100
        self.click_btn = Button(
            text="BAIL THE WATER!",
            font_size=18,
            bold=True,
            size_hint=(None, None),
            size=(btn_w, btn_h),
            pos=(
                (Window.width - btn_w) / 2,
                (Window.height - btn_h) / 2
            ),
        )
        self.click_btn.bind(on_press=self.increase_progress)
        self.game_area.add_widget(self.click_btn)

    def start_game(self, dt=None):
        self.progress = 0
        self.active = True
        self.progress_label.text = f"Progress: {self.progress}/{self.max_progress}"

    def update_bg(self, *args):
        self.bg_img.size = self.size
        self.bg_img.pos = self.pos

    def increase_progress(self, instance=None):
        if not self.active:
            return
        self.progress += 1
        self.progress_label.text = f"Progress: {self.progress}/{self.max_progress}"
        if self.progress >= self.max_progress:
            self.excursion_success("Machine Overloaded! Sabotage complete!")

class CanonLoaderMiniGame(BaseMiniGame):
    user_status_screen = ObjectProperty(None)

    def __init__(self, player, difficulty=1, **kwargs):
        super().__init__(player, difficulty, **kwargs)

        # Create main layout
        self.layout = FloatLayout()
        self.add_widget(self.layout)

        # Background - add first so it's behind everything
        self.bg_widget = Image(
            source="Assets/canon_deck.png",
            size=Window.size,
            allow_stretch=True,
            keep_ratio=False
        )
        self.layout.add_widget(self.bg_widget)

        # Set sizes
        self.canon_shot_size = (15, 15)
        self.canon_hole_size = (80, 85)

        # Create canon_shot widget (the video)
        self.canon_shot_widget = Image(
            source="Assets/canon_shot_bar.png",
            size=self.canon_shot_size
        )


        # Create canon_hole widget
        self.canon_hole_widget = Image(
            source="Assets/murderer_canon.png",
            size=self.canon_hole_size
        )
        self.layout.add_widget(self.canon_hole_widget)
        self.layout.add_widget(self.canon_shot_widget)

        # Back button
        self.back_btn = Button(
            text="Back",
            size_hint=(0.15, 0.1),
            pos_hint={'x': 0, 'y': 0}
        )
        self.back_btn.bind(on_press=self.go_back)
        self.layout.add_widget(self.back_btn)

        # Game state
        self.active = True
        self.game_completed = False

        # Input flags
        self.move_left = False
        self.move_right = False
        self.move_down = False
        self.move_up = False

        # Initialize positions - SIMPLE AND PREDICTABLE
        self.reset_positions()

        # Bind keys and start game loop
        Window.bind(on_key_down=self._on_key_down)
        Window.bind(on_key_up=self._on_key_up)
        self.event = Clock.schedule_interval(self.update, 1 / 60)

    def reset_positions(self):
        """Reset simple predictable positions"""
        self.layout.clear_widgets()  # remove all old widgets

        # Rebuild background and widgets fresh
        self.bg_widget = Image(
            source="Assets/canon_deck.png",
            size=Window.size,
            allow_stretch=True,
            keep_ratio=False
        )
        self.layout.add_widget(self.bg_widget)

        self.layout.add_widget(self.canon_shot_widget)
        self.layout.add_widget(self.canon_hole_widget)

        self.layout.add_widget(self.back_btn)

        self.game_completed = False
        self.active = True

        # canon_hole: bottom-center (easy placement)
        self.canon_hole_x = (Window.width / 2) - (self.canon_hole_size[0] / 2) # right side of the screen
        self.canon_hole_y = -50  # fixed near the bottom
        self.canon_hole_widget.size = self.canon_hole_size
        self.canon_hole_widget.pos = (self.canon_hole_x, self.canon_hole_y)

        # canon_shot: top-center
        self.canon_shot_x = (- Window.width / 2) - (self.canon_shot_size[0] / 2) + 125
        self.canon_shot_y = 200 - self.canon_shot_size[1] - 120
        self.canon_shot_widget.size = self.canon_shot_size
        self.canon_shot_widget.pos = (self.canon_shot_x, self.canon_shot_y)

        # Reset movement + speed
        self.move_left = self.move_right = self.move_down = self.move_up = False
        self.speed = 8

    def check_collision(self):
        """Simplified collision detection"""
        # Get centers of both objects
        shot_center_x = self.canon_shot_x + self.canon_shot_size[0] / 2
        shot_center_y = self.canon_shot_y + self.canon_shot_size[1] / 2
        hole_center_x = self.canon_hole_x + self.canon_hole_size[0] / 2
        hole_center_y = self.canon_hole_y + self.canon_hole_size[1] / 2

        # Check if centers are close enough (distance-based collision)
        distance_x = abs(shot_center_x - hole_center_x)
        distance_y = abs(shot_center_y - hole_center_y)

        # Collision if within combined half-sizes
        return (distance_x < (self.canon_shot_size[0] +
                              self.canon_hole_size[0]) / 2
                and
                distance_y < (self.canon_shot_size[1] +
                              self.canon_hole_size[1]) / 2)

    def update(self, dt):
        if not self.active or self.game_completed:
            return

        # Move canon_shot based on input
        if self.move_left:
            self.canon_shot_x = max(0, self.canon_shot_x - self.speed)
        if self.move_right:
            self.canon_shot_x = min(Window.width - self.canon_shot_size[0], self.canon_shot_x + self.speed)
        if self.move_down:
            self.canon_shot_y = max(0, self.canon_shot_y - self.speed)
        if self.move_up:
            self.canon_shot_y = min(Window.height - self.canon_shot_size[1], self.canon_shot_y + self.speed)

        # Update canon_shot position
        self.canon_shot_widget.pos = (self.canon_shot_x, self.canon_shot_y)

        # Check for successful delivery
        if self.check_collision():
            self.handle_success()

    def handle_success(self):
        """Handle game completion"""
        if not self.game_completed:
            self.game_completed = True
            self.excursion_success("You've loaded another shot into the canon, PREPARE TO FIRE")
            self.cleanup()

    def cleanup(self):
        """Clean up game resources"""
        self.active = False
        if self.event:
            Clock.unschedule(self.event)
            self.event = None

    def start_game(self, dt=None):
        """Start or restart the game"""
        self.cleanup()
        self.reset_positions()  # This now works predictably
        Window.bind(on_key_down=self._on_key_down)
        Window.bind(on_key_up=self._on_key_up)
        self.event = Clock.schedule_interval(self.update, 1 / 30)
        self.active = True
        self.game_completed = False

    def _on_key_down(self, window, key, scancode, codepoint, modifiers):
        if not self.active or self.game_completed:
            return

        if key == 276:  # Left
            self.move_left = True
        elif key == 275:  # Right
            self.move_right = True
        elif key == 274:  # Down
            self.move_down = True
        elif key == 273:  # Up
            self.move_up = True

    def _on_key_up(self, window, key, scancode):
        if key == 276:
            self.move_left = False
        elif key == 275:
            self.move_right = False
        elif key == 274:
            self.move_down = False
        elif key == 273:
            self.move_up = False

    def on_enter(self, *args):
        super().on_enter(*args)
        self.reset_positions()
        self.active = True
        Window.bind(on_key_down=self._on_key_down)
        Window.bind(on_key_up=self._on_key_up)
        self.event = Clock.schedule_interval(self.update, 1 / 60)

    def on_leave(self, *args):
        if self.event:
            Clock.unschedule(self.event)
            self.event = None
        Window.unbind(on_key_down=self._on_key_down)
        Window.unbind(on_key_up=self._on_key_up)

    def go_back(self, instance):
        """Return to previous screen"""
        self.cleanup()
        super().go_back(instance)

class DiceRollingMiniGame(BaseMiniGame):
    user_status_screen = ObjectProperty(None)

    def __init__(self, player, difficulty=1, **kwargs):
        super().__init__(player, difficulty, **kwargs)
        self.dice_frames = [
            "Assets/dice_one.png",
            "Assets/dice_two.png",
            "Assets/dice_three.png",
            "Assets/dice_four.png",
            "Assets/dice_five.png",
            "Assets/dice_six.png",
        ]
        self.is_rolling = False
        self.current_results = [1, 1, 1]  # Start with dice showing 1
        self.max_spins = 5
        self.spins_left = self.max_spins

        # Initialize UI components first
        self.build_game()

    def build_game(self):
        self.game_area.clear_widgets()

        # Title Image
        self.title_image = Image(
            source="Assets/demon_dice.png",
            size_hint=(1.5, 0.3),
            allow_stretch=True,
            keep_ratio=True,
            pos_hint={'center_x': 0.5}
        )

        # Background
        self.bg_img = Image(
            source="Assets/gambling_table.png",
            allow_stretch=True,
            keep_ratio=False,
            size=self.size,
            pos=self.pos
        )
        self.game_area.add_widget(self.bg_img)
        self.bind(size=self.update_bg, pos=self.update_bg)

        # Layout for the canon_hole machine
        self.main_layout = BoxLayout(orientation="vertical", spacing=15, padding=30)

        # Title
        title = Label(
            text="\n Match numbers to win!\n One match is $50,000\n Two matches are $150,000\n Three matches are $500,000",
            font_size=24,
            bold=True,
            size_hint=(1, 0.8),
            halign="center",
            valign="top"
        )
        title.bind(size=title.setter('text_size'))
        self.main_layout.add_widget(self.title_image)
        self.main_layout.add_widget(title)

        # Number of spins allowed
        self.spins_left = self.max_spins

        # Columns (3 dice)
        self.columns = []
        reels_layout = BoxLayout(orientation="horizontal", spacing=20)

        preset_numbers = ["6", "6", "6"]

        for i, preset in enumerate(preset_numbers):
            col = BoxLayout(orientation="vertical", spacing=10)

            # Preset number on top
            preset_lbl = Label(text=preset, font_size=30, bold=True, color=(1, 1, 1, 1))
            col.add_widget(preset_lbl)

            # Dice image with animation capability
            dice_image = Image(
                source=self.dice_frames[0],  # Start with dice one
                size_hint=(None, None),
                size=(110, 110),
                pos_hint={'center_x': 0.5},
                allow_stretch=True,
                keep_ratio=True
            )
            col.dice_image = dice_image
            col.preset_value = int(preset)
            col.current_value = 1

            col.add_widget(dice_image)
            self.columns.append(col)
            reels_layout.add_widget(col)

        self.main_layout.add_widget(reels_layout)

        # Spin button
        self.spin_btn = Button(text=f"Roll Dice ({self.spins_left} left)", size_hint=(.3, 0.35), pos_hint={'center_x': 0.5})
        self.spin_btn.bind(on_press=self.roll_dice)
        self.main_layout.add_widget(self.spin_btn)

        self.game_area.add_widget(self.main_layout)

        # Initialize game state after UI is built
        self.reset_game_state()

    def start_game(self, dt=None):
        """Now just a wrapper for reset_game_state for compatibility"""
        self.reset_game_state()

    def reset_game_state(self):
        """Reset the game to initial state"""
        self.spins_left = self.max_spins
        self.is_rolling = False

        # Only update spin_btn if it exists
        if hasattr(self, 'spin_btn'):
            self.spin_btn.text = f"Roll Dice ({self.spins_left} left)"
            self.spin_btn.disabled = False

        # Reset dice to show 1
        if hasattr(self, 'columns'):
            for col in self.columns:
                col.dice_image.source = self.dice_frames[0]
                col.current_value = 1

    def roll_dice(self, instance=None):
        if self.spins_left <= 0 or self.is_rolling:
            return

        self.is_rolling = True
        self.spin_btn.disabled = True

        # Start animation for all dice
        for i, col in enumerate(self.columns):
            self.animate_dice_roll(col, i)

    def animate_dice_roll(self, dice_column, index, frame_count=0, max_frames=20):
        """Animate dice rolling with rotation and frame changes"""
        if frame_count >= max_frames:
            # Final result
            final_value = random.randint(1, 6)
            dice_column.current_value = final_value
            dice_column.dice_image.source = self.dice_frames[final_value - 1]

            # Remove rotation
            dice_column.dice_image.canvas.before.clear()
            dice_column.dice_image.canvas.after.clear()

            # Check if all dice have finished rolling
            if all(hasattr(col, 'current_value') for col in self.columns):
                self.finish_roll()
            return

        # Continue animation
        current_frame = frame_count % 6
        dice_column.dice_image.source = self.dice_frames[current_frame]

        # Add rotation effect
        rotation_angle = (frame_count * 30) % 360  # Rotate 30 degrees per frame
        dice_column.dice_image.canvas.before.clear()
        dice_column.dice_image.canvas.after.clear()

        with dice_column.dice_image.canvas.before:
            PushMatrix()
            Rotate(angle=rotation_angle, origin=dice_column.dice_image.center)

        with dice_column.dice_image.canvas.after:
            PopMatrix()

        # Schedule next frame
        Clock.schedule_once(
            lambda dt: self.animate_dice_roll(dice_column, index, frame_count + 1, max_frames),
            0.1  # 100ms between frames for smooth animation
        )

    def finish_roll(self):
        """Handle the results after dice finish rolling"""
        self.is_rolling = False
        self.spins_left -= 1

        # Get final results
        results = [col.current_value for col in self.columns]
        preset_values = [col.preset_value for col in self.columns]

        # Count matches
        matches = sum(1 for preset, result in zip(preset_values, results) if result == preset)

        # Determine outcome
        if matches == 3:
            reward = 500000
            message = "Jackpot! 3 matches! +$500,000"
            self.player.gold += reward
            self.spin_btn.disabled = True
            self.show_result_popup(message, success=True)
        elif matches == 2:
            reward = 150000
            message = "Excellent! 2 matches! +$150,000"
            self.player.gold += reward
            self.spin_btn.disabled = True
            self.show_result_popup(message, success=True)
        elif matches == 1:
            reward = 50000
            message = "Good! 1 match! +$50,000"
            self.player.gold += reward
            self.spin_btn.disabled = True
            self.show_result_popup(message, success=True)
        else:
            if self.spins_left == 0:
                penalty = 10000
                message = "No matches! You lost $10,000!"
                self.player.gold -= penalty
                self.spin_btn.disabled = True
                self.show_result_popup(message, success=False)
            else:
                self.spin_btn.text = f"Roll Dice ({self.spins_left} left)"
                self.spin_btn.disabled = False

    def show_result_popup(self, message, success=True):
        """Show result popup with continue button"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=20)

        result_label = Label(
            text=message,
            font_size=20,
            halign='center',
            valign='middle'
        )
        result_label.bind(size=result_label.setter('text_size'))
        content.add_widget(result_label)

        continue_btn = Button(
            text="Continue",
            size_hint_y=None,
            height=50
        )
        content.add_widget(continue_btn)

        popup = Popup(
            title="Roll Results" if success else "Better Luck Next Time",
            content=content,
            size_hint=(0.7, 0.5)
        )

        if success:
            def on_continue(instance):
                popup.dismiss()
                self.excursion_success(message)

            continue_btn.bind(on_press=on_continue)
        else:
            def on_continue(instance):
                popup.dismiss()
                self.excursion_fail(message)

            continue_btn.bind(on_press=on_continue)

        popup.open()

    def update_bg(self, *args):
        self.bg_img.size = self.size
        self.bg_img.pos = self.pos

    def on_enter(self, *args):
        super().on_enter(*args)
        # Game is already initialized in __init__, so we just ensure state is reset
        self.reset_game_state()

    def on_leave(self, *args):
        self.reset_game_state()
        super().on_leave(*args)

class SeaBattleMiniGame(BaseMiniGame):
    user_status_screen = ObjectProperty(None)

    def __init__(self, player, difficulty=1, **kwargs):
        super().__init__(player, difficulty, **kwargs)
        self.difficulty = difficulty

    def build_game(self):
        self.game_area.clear_widgets()
        self.layout = FloatLayout()
        self.game_area.add_widget(self.layout)

        # Background
        self.bg = Image(source="Assets/armada.png",
                        allow_stretch=True, keep_ratio=False,
                        size=Window.size, pos=(0, 0))
        self.layout.add_widget(self.bg)

        # Player ship (use Image so PNG alpha is preserved; not a Button)
        self.ship_image = "Assets/galleon.png"
        ship_w, ship_h = 120, 80
        start_x = Window.width // 2 - ship_w // 2
        # lock starting Y to bottom 30% range
        max_y = int(Window.height * 0.3) - ship_h
        start_y = max(10, max_y // 2)
        self.ship = Image(source=self.ship_image,
                          size_hint=(None, None),
                          size=(ship_w, ship_h),
                          pos=(start_x, start_y)
                          )
        self.layout.add_widget(self.ship)

        # HUD
        self.score = 0;
        self.lives = 3;
        self.timer = 30
        self.hud = Label(text=f"Score: {self.score}  Time: {int(self.timer)}",
                         pos=(20, Window.height - 40),
                         size_hint=(None, None))
        self.layout.add_widget(self.hud)

        # Boats (use Image so they look like ships)
        self.boats = []
        min_y = int(Window.height * 0.35)
        max_y = int(Window.height * 0.55)
        for _ in range(3 + self.difficulty):
            boat_w, boat_h = 120, 100
            bx = random.randint(0, Window.width - boat_w)
            by = random.randint(min_y, max_y - boat_h)
            boat = Image(source="Assets/galleon.png",
                         size_hint=(None, None),
                         size=(boat_w, boat_h),
                         pos=(bx, by))
            # attributes for enemy firing/timers
            boat.cooldown = random.uniform(1.5, 3.5)
            boat.time_since_last_shot = 0.0
            boat.vx = random.choice([-1, 1]) * random.uniform(0.5, 1.5)  # optional horizontal drift
            self.boats.append(boat)
            self.layout.add_widget(boat)

        # Projectiles container
        self.bullets = []

        # Ensure ship bounds are set (use for clamping later)
        self.ship_w, self.ship_h = ship_w, ship_h

        # HUD
        self.score = 0
        self.lives = 3
        self.timer = 30
        self.hud = Label(
            text=f"Score: {self.score}  Time: {int(self.timer)}",
            pos=(20, Window.height - 40),  # Use Window.height instead of HEIGHT
            size_hint=(None, None)
        )
        self.layout.add_widget(self.hud)

    def start_game(self, dt=None):
        self.build_game()  # Rebuild the game elements
        self.active = True
        # Input + Clock
        Window.bind(on_key_down=self.on_key_down)
        self.event = Clock.schedule_interval(self.update, 1 / 30.0)

    def on_key_down(self, window, key, scancode, codepoint, modifiers):
        if not self.active:
            return
        step = 15
        x, y = self.ship.pos
        moved = False
        if key == 273:  # Up
            y += step;
            moved = True
        elif key == 274:  # Down
            y -= step;
            moved = True
        elif key == 276:  # Left
            x -= step;
            moved = True
        elif key == 275:  # Right
            x += step;
            moved = True
        elif key == 32:  # Space
            self.shoot()

        # Lock ship to bottom 30% of screen
        max_y = int(Window.height * 0.3) - self.ship_h
        x = max(0, min(Window.width - self.ship_w, x))
        y = max(0, min(max_y, y))
        self.ship.pos = (x, y)

    def get_projectile_image(self):
        # If player's portfolio structure is dict-like, adapt this to your data.
        for name, (units, total_cost) in self.player.portfolio.items():
            # if your items are dicts you'll need to iterate appropriately
            # This is a fallback pattern — adapt to your actual portfolio structure
            if "canon_shot" in name.lower():
                # assume PNG is stored in Assets using name mapping
                return f"Assets/{name}.png"
        return "Assets/canon_shot_round.png"

    def shoot(self):
        if not self.active:
            return
        image_source = self.get_projectile_image()
        # spawn bullet at ship's nose (approx)
        bx = self.ship.center_x - 10
        by = self.ship.top  # spawn above the ship
        bullet = Image(source=image_source,
                       size_hint=(None, None),
                       size=(20, 20),
                       pos=(bx, by))
        # Player bullets go UP the screen
        bullet.dx = 0.0
        bullet.dy = +10.0
        bullet.rotation_angle = 0.0
        bullet.is_enemy = False
        self.bullets.append(bullet)
        self.layout.add_widget(bullet)

    def fire_enemy_projectile(self, boat):
        bx = boat.center_x - 10
        by = boat.y  # spawn roughly from top of the boat
        bullet = Image(source="Assets/canon_shot_round.png",
                       size_hint=(None, None),
                       size=(20, 20),
                       pos=(bx, by))
        bullet.dx = 0.0
        bullet.dy = -6.0  # enemy bullets go down
        bullet.rotation_angle = 0.0
        bullet.is_enemy = True
        self.bullets.append(bullet)
        self.layout.add_widget(bullet)

    def update(self, dt):
        if not self.active:
            return

        # Enemy shooting and (optional) horizontal drift inside locked band
        for boat in list(self.boats):
            boat.time_since_last_shot += dt
            if boat.time_since_last_shot >= boat.cooldown:
                boat.time_since_last_shot = 0.0
                self.fire_enemy_projectile(boat)
            # optional drift & keep boats inside 35%-55% band
            bx, by = boat.pos
            bx += boat.vx
            if bx < 0 or bx > Window.width - boat.width:
                boat.vx *= -1
            # clamp vertical to band in case random changed it
            min_y = int(Window.height * 0.35)
            max_y = int(Window.height * 0.55) - boat.height
            by = max(min_y, min(max_y, by))
            boat.pos = (bx, by)

        # Move bullets and rotate visually (no effect on collisions)
        for bullet in list(self.bullets):
            bullet.x += bullet.dx
            bullet.y += bullet.dy

            # visual rotation
            bullet.rotation_angle = (getattr(bullet, "rotation_angle", 0) + 10) % 360
            bullet.canvas.before.clear()
            with bullet.canvas.before:
                PushMatrix()
                Rotate(angle=bullet.rotation_angle, origin=bullet.center)
            bullet.canvas.after.clear()
            with bullet.canvas.after:
                PopMatrix()

            # Remove off-screen bullets
            if (bullet.x < -50 or bullet.y < -50 or
                    bullet.x > Window.width + 50 or bullet.y > Window.height + 50):
                try:
                    self.layout.remove_widget(bullet)
                except Exception:
                    pass
                if bullet in self.bullets:
                    self.bullets.remove(bullet)

        # Collisions (bullet -> boats)
        for bullet in list(self.bullets):
            if not getattr(bullet, "is_enemy", False):
                for boat in list(self.boats):
                    if bullet.collide_widget(boat):
                        self.score += 100
                        try:
                            self.layout.remove_widget(bullet)
                            self.layout.remove_widget(boat)
                        except Exception:
                            pass
                        if bullet in self.bullets:
                            self.bullets.remove(bullet)
                        if boat in self.boats:
                            self.boats.remove(boat)
                        break
            else:
                # enemy bullet hits player ship
                if bullet.collide_widget(self.ship):
                    try:
                        self.layout.remove_widget(bullet)
                    except Exception:
                        pass
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    self.player.durability_current = max(0, self.player.durability_current - 5)
                    if self.player.durability_current <= 0:
                        self.excursion_fail("Your ship was sunk! The ocean claims her due.")

    def on_enter(self, *args):
        super().on_enter(*args)
        self.start_game()

    def on_leave(self, *args):
        if self.event:
            Clock.unschedule(self.event)
            self.event = None
        Window.unbind(on_key_down=self.on_key_down)
        self.reset_game_state()

    def reset_game_state(self):
        super().reset_game_state()
        # Reset game-specific variables
        self.score = 0
        self.lives = 3
        self.timer = 30
        self.boats = []
        self.bullets = []
        self.current_frame = 0

class PearlDiverMiniGame(BaseMiniGame):
    user_status_screen = ObjectProperty(None)

    def __init__(self, player, difficulty=1, **kwargs):
        super().__init__(player, difficulty, **kwargs)
        self.difficulty = difficulty
        self.swim_images = [
            "Assets/swim_down_stroke.png",
            "Assets/swim_upstroke.png",
            "Assets/swim_twist.png",
            "Assets/swim_down_stroke.png",
            "Assets/swim_twist_down.png",
            "Assets/swim_twist_up.png"
        ]

        self.current_frame = 0
        self.frame_timer = 0
        self.frame_speed = 0.15

        # Ship-like movement variables
        self.player_angle = 1  # Current facing angle (degrees)
        self.player_speed = 0  # Current movement speed
        self.max_speed = 2 + player.speed * 3  # Based on fleet speed
        self.acceleration = 1.8
        self.deceleration = 0.25
        self.turn_speed = 4.5  # Turning rate
        self.pearl_multiplier = 1.2 #120% bonus

        # Position
        self.player_x = Window.width // 2
        self.player_y = 50

    def build_game(self):
        self.game_area.clear_widgets()
        self.layout = FloatLayout()
        self.game_area.add_widget(self.layout)
        self.pearls = []

        # Background
        self.bg = Image(
            source="Assets/ship_wreck.png",
            allow_stretch=True,
            keep_ratio=False,
            size=Window.size,
            pos=(0, 0)
        )
        self.layout.add_widget(self.bg)

        # Player (image only) - centered for rotation
        # Reset player position with safe buffer
        self.player_x = Window.width // 2
        self.player_y = 100

        self.player_widget = Image(
            source=self.swim_images[0],
            size_hint=(None, None),
            size=(95, 95),
            pos=(self.player_x - 45, self.player_y - 45),
        )
        self.layout.add_widget(self.player_widget)

        # Speed and multiplier indicator
        self.speed_label = Label(
            text=f"Speed: {self.player_speed:.1f} Multiplier: x{self.pearl_multiplier:.2f}",
            font_size=Window.width * 0.02,
            size_hint=(None, None),
            bold=True,
            color=(0, 0.1, 0, 1),
            pos=(20, Window.height - 80),
        )
        self.layout.add_widget(self.speed_label)

        # Sharks with safe spawning (avoid player area)
        self.sharks = []
        safe_zone_radius = 200  # 200 pixel safe zone around player

        for _ in range(3 + self.difficulty):
            # Try multiple positions to find one outside safe zone
            for attempt in range(5):  # Try up to 5 times to find a safe spot
                x = random.randint(0, Window.width - 60)
                y = random.randint(Window.height // 2, Window.height - 60)

                # Check if this position is outside the safe zone
                distance_to_player = math.hypot(x - self.player_x, y - self.player_y)
                if distance_to_player > safe_zone_radius:
                    break
            else:
                pass

            shark = Button(
                background_normal="Assets/shark_body.png",
                size_hint=(None, None),
                size=(90, 90),
                pos=(x, y),
            )
            angle = random.uniform(0, 2 * math.pi)
            shark.dx = math.cos(angle) * (2 + self.difficulty)
            shark.dy = math.sin(angle) * (2 + self.difficulty)
            self.sharks.append(shark)
            self.layout.add_widget(shark)

        # Pearls also with safe spawning
        for _ in range(5):
            # Try to place pearls away from player start
            for attempt in range(5):
                x = random.randint(50, Window.width - 50)
                y = random.randint(150, Window.height - 200)  # Start higher to avoid player area
                distance_to_player = math.hypot(x - self.player_x, y - self.player_y)
                if distance_to_player > 150:  # At least 150 pixels from player
                    break

            pearl = Image(
                source="Assets/pearl.png",
                size_hint=(None, None),
                size=(40, 40),
                pos=(x, y),
                color=(1, 1, 1, 1),
            )
            self.layout.add_widget(pearl)
            self.pearls.append(pearl)

        # Timer
        self.time_left = 20
        self.timer_label = Label(
            text=f"Time Left: {int(self.time_left)}",
            font_size=Window.width * 0.03,
            size_hint=(None, None),
            bold=True,
            color=(0, 0.1, 0, 1),
            pos=(Window.width - 500, Window.height - 80),
        )
        self.layout.add_widget(self.timer_label)

    def start_game(self, dt=None):
        self.build_game()
        self.active = True
        Window.bind(on_key_down=self.on_key_down)
        self.event = Clock.schedule_interval(self.update, 1 / 30)

    def on_key_down(self, window, key, scancode, codepoint, modifiers):
        if not self.active:
            return

        # Up/Down = Accelerate/Decelerate
        # Left/Right = Turn
        if key == 273:  # Up - Accelerate
            self.player_speed = min(self.max_speed, self.player_speed + self.acceleration)
            print(f"DEBUG: Accelerating - Speed: {self.player_speed:.1f}")
        elif key == 274:  # Down - Decelerate/Brake
            self.player_speed = max(0, self.player_speed - self.deceleration * 2)
            print(f"DEBUG: Braking - Speed: {self.player_speed:.1f}")
        elif key == 276:  # Left - Turn left (should increase angle)
            self.player_angle -= self.turn_speed  # FIXED: Changed from -= to +
            print(f"DEBUG: Turning LEFT - Angle: {self.player_angle:.1f}°")
        elif key == 275:  # Right - Turn right (should decrease angle)
            self.player_angle += self.turn_speed  # FIXED: Changed from += to -
            print(f"DEBUG: Turning RIGHT - Angle: {self.player_angle:.1f}°")

    def reset_game_state(self):
        """Properly reset the game state"""
        super().reset_game_state()

        # Reset game variables
        self.time_left = 20
        self.sharks = []
        self.pearls = []
        self.player_speed = 0
        self.player_angle = 0
        self.pearl_multiplier = 1.2  # Reset multiplier to base value

        # Clear the layout properly
        if hasattr(self, 'layout'):
            self.layout.clear_widgets()

        # Rebuild the game
        self.build_game()

    def update(self, dt):
        if not self.active:
            return

        # Apply natural deceleration
        if self.player_speed > 0:
            self.player_speed = max(0, self.player_speed - self.deceleration * 0.13)

        # Update position based on current angle and speed
        if self.player_speed > 0:
            angle_rad = math.radians(self.player_angle)
            self.player_x -= math.cos(angle_rad) * self.player_speed
            self.player_y += math.sin(angle_rad) * self.player_speed

            # Screen wrapping
            if self.player_x < -self.player_widget.width:
                self.player_x = Window.width
            elif self.player_x > Window.width:
                self.player_x = -self.player_widget.width
            if self.player_y < -self.player_widget.height:
                self.player_y = Window.height
            elif self.player_y > Window.height:
                self.player_y = -self.player_widget.height

        # Update player widget position (centered)
        self.player_widget.pos = (self.player_x - 45, self.player_y - 45)

        # Animation
        self.frame_timer += dt
        if self.frame_timer >= self.frame_speed:
            self.frame_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.swim_images)
            self.player_widget.source = self.swim_images[self.current_frame]

        # Apply rotation to face movement direction
        self.player_widget.canvas.before.clear()
        self.player_widget.canvas.after.clear()

        with self.player_widget.canvas.before:
            PushMatrix()
            Rotate(angle=-self.player_angle, origin=self.player_widget.center)

        with self.player_widget.canvas.after:
            PopMatrix()

        # Update speed and multiplier display in real-time
        if hasattr(self, 'speed_label'):
            self.speed_label.text = f"Speed: {self.player_speed:.1f} \nMultiplier: x{self.pearl_multiplier:.2f}"

        # Pearl effects
        if hasattr(self, "pearls"):
            for pearl in self.pearls:
                self.apply_hue_shift(pearl, self.time_left)

        # Move sharks
        px, py = self.player_widget.center
        for shark in self.sharks:
            x, y = shark.pos
            x += shark.dx
            y += shark.dy
            if x <= 0 or x >= Window.width - shark.width:
                shark.dx *= -1
            if y <= 0 or y >= Window.height - shark.height:
                shark.dy *= -1
            shark.pos = (x, y)

            dist = math.hypot(px - shark.center_x, py - shark.center_y)
            if dist < (shark.width * 0.35 + self.player_widget.width * 0.35):
                self.excursion_fail("You were eaten by a curious shark!")
                return

        # Timer
        self.time_left -= dt
        if hasattr(self, 'timer_label'):
            self.timer_label.text = f"Time Left: {int(self.time_left)}"

        # Game completion with rewards
        if self.time_left <= 0:
            base_reward = 50000
            final_reward = int(base_reward * self.pearl_multiplier)
            self.player.gold += final_reward

            self.excursion_success(
                f"You survived the Pearl Diving!\n"
                f"Pearls Collected: {5 - len(self.pearls)}\n"
                f"Base Reward: ${base_reward:,}\n"
                f"Pearl Multiplier: x{self.pearl_multiplier:.2f}\n"
                f"Total Earned: ${final_reward:,}"
            )

        # Pearl collection
        if hasattr(self, "pearls"):
            for pearl in self.pearls[:]:
                dist = math.hypot(px - pearl.center_x, py - pearl.center_y)
                if dist < (self.player_widget.width * 0.4):
                    # Each pearl adds 1.2 to multiplier max 7.2x reward
                    self.pearl_multiplier += 1.2
                    self.layout.remove_widget(pearl)
                    self.pearls.remove(pearl)

                    # Update multiplier display immediately
                    if hasattr(self, 'speed_label'):
                        self.speed_label.text = f"Speed: {self.player_speed:.1f} | Multiplier: x{self.pearl_multiplier:.2f}"

                    print(f"Pearl collected! Multiplier now: x{self.pearl_multiplier:.2f}")

    def apply_hue_shift(self, image_widget, time, speed=2.0):
        hue = (math.sin(time * speed) + 1) / 2.0
        color = colorsys.hsv_to_rgb(hue, 0.6, 1.0)
        image_widget.color = (*color, 1)

    def on_enter(self, *args):
        super().on_enter(*args)

        self.start_game()
        Window.bind(on_key_down=self.on_key_down)

    def on_leave(self, *args):
        if self.event:
            Clock.unschedule(self.event)
            self.event = None
        Window.unbind(on_key_down=self.on_key_down)
        self.reset_game_state()

class MainMenu(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

# --- App ---
class BarelySober1592(App):
    def build(self):
        return

if __name__ == "__main__":
    BarelySober1592().run()