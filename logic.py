# logic.py
import random
from datetime import datetime, timedelta
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from database import items

class Player:
    def __init__(self, name="Player"):
        self.name = name
        self.gold = 15000
        self.portfolio = {}
        self.awareness = 0
        self.dehydration_awareness = 0
        self.emergency_hydration = 100
        self.combat_power = 10
        self.heading = 0
        self._speed = 2
        self._current_speed = 1
        self.capacity = 1

        # Ship-related
        self.fleet = []  # list of ship dicts
        self.current_ship = None
        self.sails = 2
        self.navigation_items = []
        self.ship_capacity = 1
        self.base_ship_speed = 4
        self.dehydration_penalty = 0
        self.durability_max = 100
        self.durability_current = 100
        self.game_time = datetime(1592, 6, 6, 6, 0)

    #--------------------------
    # SAVE & LOAD METHODS
    #--------------------------
    def to_dict(self):
        """Serialize the player state to a JSON-friendly dictionary."""
        return {
            "name": self.name,
            "gold": self.gold,
            "portfolio": {k: list(v) for k, v in self.portfolio.items()},
            "dehydration_awareness": self.dehydration_awareness,
            "emergency_hydration": self.emergency_hydration,
            "combat_power": self.combat_power,
            "heading": self.heading,
            "_speed": self._speed,
            "_current_speed": self._current_speed,
            "capacity": self.capacity,
            "fleet": self.fleet,
            "current_ship": self.current_ship,
            "sails": self.sails,
            "navigation_items": self.navigation_items,
            "ship_capacity": self.ship_capacity,
            "base_ship_speed": self.base_ship_speed,
            "dehydration_penalty": self.dehydration_penalty,
            "durability_max": self.durability_max,
            "durability_current": self.durability_current,
            "game_time": self.game_time.isoformat(),
        }

    @classmethod
    def from_dict(cls, data):
        """Rebuild a Player object from a saved state dict."""
        player = cls(name=data.get("name", "Player"))
        player.gold = data.get("gold", 15000)
        player.portfolio = {
            k: tuple(v) if isinstance(v, (list, tuple)) else (v, v)
            for k, v in data.get("portfolio", {}).items()
        }
        player.dehydration_awareness = data.get("dehydration_awareness", 0)
        player.emergency_hydration = data.get("emergency_hydration", 100)
        player.combat_power = data.get("combat_power", 10)
        player.heading = data.get("heading", 0)
        player._speed = data.get("_speed", 2)
        player._current_speed = data.get("_current_speed", 1)
        player.capacity = data.get("capacity", 1)
        player.fleet = data.get("fleet", [])
        player.current_ship = data.get("current_ship", None)
        player.sails = data.get("sails", 2)
        player.navigation_items = data.get("navigation_items", [])
        player.ship_capacity = data.get("ship_capacity", 1)
        player.base_ship_speed = data.get("base_ship_speed", 4)
        player.dehydration_penalty = data.get("dehydration_penalty", 0)
        player.durability_max = data.get("durability_max", 100)
        player.durability_current = data.get("durability_current", 100)
        player.game_time = datetime.fromisoformat(data.get("game_time"))
        return player

    def debug_portfolio(self):
        """Debug method to check portfolio structure"""
        print("\n=== PORTFOLIO DEBUG ===")
        for item_name, quantity_data in self.portfolio.items():
            print(f"Item: {item_name}, Quantity data: {quantity_data}, Type: {type(quantity_data)}")
        print("=======================\n")

    def clear_fleet(self):
        """Clear the fleet completely"""
        self.fleet = []

    def show_message(self, title, text):
        layout = BoxLayout(orientation="vertical", padding=10)
        layout.add_widget(Label(text=text, halign="center"))
        popup = Popup(title=title, content=layout, size_hint=(0.6, 0.4))
        popup.open()

    def advance_day(self):
        self.game_time += timedelta(days=1)

    def get_navigation_bonus(self):
        """Calculate total navigation bonus with persistent random multipliers."""
        total_bonus = 0.0

        # Initialize storage for individual item bonuses if it doesn't exist
        if not hasattr(self, 'item_bonuses'):
            self.item_bonuses = {}  # Format: {item_name: [bonus1, bonus2, ...]}

        # Loop through player's owned items
        for item_name, quantity_data in self.portfolio.items():
            # Handle quantity whether it's an int or tuple
            if isinstance(quantity_data, tuple):
                # If it's a tuple, take the first element as quantity
                quantity = quantity_data[0] if quantity_data else 0
            else:
                quantity = int(quantity_data)

            # Find that item in the database
            for db_item in items:
                if db_item["name"] == item_name and db_item["sector"] == "Navigation":
                    effect_range = db_item["effect"]

                    # Initialize bonuses list for this item if needed
                    if item_name not in self.item_bonuses:
                        self.item_bonuses[item_name] = []

                    # Ensure we have the right number of bonuses for current quantity
                    current_bonuses = self.item_bonuses[item_name]

                    # Add new random bonuses if we have more items than bonuses
                    while len(current_bonuses) < quantity:
                        if isinstance(effect_range, (list, tuple)) and len(effect_range) >= 2:
                            min_effect = float(effect_range[0])
                            max_effect = float(effect_range[1])
                            import random
                            new_bonus = random.uniform(min_effect, max_effect)
                            current_bonuses.append(new_bonus)
                        else:
                            current_bonuses.append(float(effect_range))

                    # Remove excess bonuses if we have fewer items than bonuses
                    while len(current_bonuses) > quantity:
                        removed_bonus = current_bonuses.pop()

                    # Sum all bonuses for this item
                    total_bonus += sum(current_bonuses)

        return total_bonus

    def print_detailed_navigation_bonuses(self):
        """Print detailed breakdown of navigation bonuses."""
        if not hasattr(self, 'item_bonuses'):
            print("No navigation bonuses calculated yet.")
            return

        print("\n=== NAVIGATION BONUS BREAKDOWN ===")
        total_bonus = 0.0

        for item_name, bonuses in self.item_bonuses.items():
            if bonuses:
                item_total = sum(bonuses)
                total_bonus += item_total
                bonus_details = ", ".join([f"+{b:.2f}%" for b in bonuses])
                print(f"{item_name} ({len(bonuses)}): {bonus_details} = +{item_total:.2f}%")

        print(f"TOTAL NAVIGATION BONUS: +{total_bonus:.2f}%")
        print("=================================\n")

    def update_item_prices(self, items):
        """Safe price updates - won't crash if items are missing prices."""
        for item in items:
            # Skip if no price key or if price isn't a number
            if 'price' not in item:
                continue

            try:
                # Make sure price is a number
                current_price = float(item["price"])

                # Get price change range
                trend = item.get("trend", (0, 0))
                if isinstance(trend, (list, tuple)) and len(trend) == 2:
                    min_change, max_change = trend
                else:
                    min_change, max_change = (0, 0)

                # Apply random change
                change = random.uniform(min_change, max_change)
                item["price"] = max(0.01, current_price + change)

            except (ValueError, TypeError):
                # If price is invalid, set a safe default
                item["price"] = 10.0

    def validate_items_data():
        """Check and fix items data structure."""
        global items

        print("=== VALIDATING ITEMS DATA ===")
        fixed_count = 0
        problematic_items = []

        for i, item in enumerate(items):
            # Check for required keys
            if 'price' not in item:
                print(f"FIXING: Item {i} '{item.get('name', 'Unknown')}' missing price")
                item['price'] = 10  # Default price
                fixed_count += 1
                problematic_items.append(item.get('name', f"Item_{i}"))

            # Ensure all required keys with defaults
            item.setdefault('name', f'Unknown_Item_{i}')
            item.setdefault('sector', 'General')
            item.setdefault('effect', (0, 0))
            item.setdefault('png', 'default.png')
            item.setdefault('description', 'No description available.')
            item.setdefault('trend', (0, 0))

        print(f"Fixed {fixed_count} items with issues")
        if problematic_items:
            print(f"Problematic items: {problematic_items}")
        print("=============================")

        return items

    def buy_item(self, item, units):
        """Fixed method that returns (success, message) tuple"""
        try:
            units = int(units)
            if units <= 0:
                return False, "Number of units must be positive"

            total_cost = item["price"] * units

            if self.gold < total_cost:
                return False, f"Insufficient funds. Need ${total_cost:.2f}, but only have ${self.gold:.2f}"

            # Process purchase
            self.gold -= total_cost
            item_name = item["name"]

            # Update portfolio
            if item_name in self.portfolio:
                current_units, current_cost = self.portfolio[item_name]
                self.portfolio[item_name] = (current_units + units, current_cost + total_cost)
            else:
                self.portfolio[item_name] = (units, total_cost)

            # Handle navigation items and storage items
            if any(word in item_name for word in ["Sail", "Compass", "Astrolabe", "Sextant", "Map"]):
                self.navigation_items.append(item_name)
                self.recalc_ship_speed()

            # If it's a storage item, recalc capacity
            if item.get("sector") == "Storage":
                self.recalc_ship_capacity()

            self.advance_day()
            self.debug_portfolio()
            return True, f"Purchased {units} units of {item_name} for ${total_cost:.2f}"

        except ValueError:
            return False, "Please enter a valid number of units"
        except Exception as e:
            return False, f"Error during purchase: {str(e)}"

    def get_durability_percentage(self):
        """Fallback for old durability calls. Uses fleet durability if available."""
        try:
            if hasattr(self, "get_fleet_durability_percentage"):
                return self.get_fleet_durability_percentage()
            elif hasattr(self, "durability_current") and hasattr(self, "durability_max"):
                return (self.durability_current / self.durability_max) * 100
            else:
                return 100
        except ZeroDivisionError:
            return 100

    def get_combat_damage_bonus(self):
        """Calculate damage bonus from combat items"""
        damage_bonus = 0
        for item_name, quantity in self.cargo_hold.items():
            item_data = self.get_item_data(item_name)  # You'll need to implement this
            if item_data and item_data.get('sector') == 'Combat':
                # Scale damage bonus based on item effect
                avg_effect = (item_data['effect_min'] + item_data['effect_max']) / 2
                damage_bonus += avg_effect * quantity * 0.1  # Adjust multiplier as needed
        return damage_bonus

    def get_combat_accuracy_bonus(self):
        """Calculate accuracy bonus from navigation/combat items"""
        accuracy_bonus = 0
        for item_name, (quantity, _) in self.portfolio.items():
            item_data = self.get_item_data(item_name)  # You'll need to implement this
            if item_data:
                if item_data.get('sector') == 'Navigation':
                    # Navigation items help aiming
                    avg_effect = (item_data['effect_min'] + item_data['effect_max']) / 2
                    accuracy_bonus += avg_effect * quantity * 0.05
                elif item_data.get('sector') == 'Combat':
                    # Some combat items might help accuracy
                    if "rifle" in item_name.lower() or "pistol" in item_name.lower():
                        accuracy_bonus += 5 * quantity
        return accuracy_bonus

    def get_reload_bonus(self):
        """Calculate reload speed bonus from crew and items"""
        reload_bonus = 0
        # Crew helps with reloading
        reload_bonus += min(self.ship_capacity * 0.1, 2.0)  # Max 2 second bonus

        # Specific items might help
        for item_name, quantity in self.portfolio.items():
            if "powder" in item_name.lower() or "ammo" in item_name.lower():
                reload_bonus += 0.5 * quantity

        return min(reload_bonus, 3.0)  # Cap at 3 second bonus

    def sell_item(self, item, units):
        self.populate_tabs()
        self.portfolio()

        """Fixed method that returns (success, message) tuple"""
        try:
            units = int(units)
            if units <= 0:
                return False, "Number of units must be positive"

            item_name = item["name"]
            if item_name not in self.portfolio:
                return False, f"You don't own any units of {item_name}"

            owned_units, total_cost = self.portfolio[item_name]
            if units > owned_units:
                return False, f"You only own {owned_units} units of {item_name}"

            # Calculate proceeds
            proceeds = units * item["price"]
            self.gold += proceeds

            # Update portfolio
            remaining_units = owned_units - units
            if remaining_units > 0:
                # Recalculate average cost for remaining units
                avg_cost_per_share = total_cost / owned_units
                remaining_cost = avg_cost_per_share * remaining_units
                self.portfolio[item_name] = (remaining_units, remaining_cost)
            else:
                del self.portfolio[item_name]

            self.advance_day()
            # After buy/sell operations, call:
            self.debug_portfolio()
            return True, f"Sold {units} units of {item_name} for ${proceeds:.2f}"

        except ValueError:
            return False, "Please enter a valid number of units"
        except Exception as e:
            return False, f"Error during sale: {str(e)}"

    # logic.py - Fix the add_item method
    def add_item(self, item_name, quantity=1):
        """Collects an item without affecting gold."""
        # Handle both string item names and dictionary items
        if isinstance(item_name, dict):
            item_name = item_name['name']  # Extract name from dictionary

        if item_name in self.portfolio:
            units, total_cost = self.portfolio[item_name]
            self.portfolio[item_name] = (units + quantity, total_cost)
        else:
            self.portfolio[item_name] = (quantity, 0)

        self.advance_day()
        return True, f"Collected {quantity}x {item_name}."

    def _update_portfolio(self, item_name, units, total_cost):
        """Updates or creates an entry in the player's portfolio."""
        if item_name in self.portfolio:
            prev_units, prev_total = self.portfolio[item_name]
            new_total_units = prev_units + units
            new_total_cost = prev_total + total_cost
            self.portfolio[item_name] = (new_total_units, new_total_cost)
        else:
            self.portfolio[item_name] = (units, total_cost)
            self.debug_portfolio()

    def has_drink_items(self, items_db):
        """Check if player owns any Drink sector items"""
        for item_name, (units, cost) in self.portfolio.items():
            if units > 0:
                for item_data in items_db:
                    if item_data["name"] == item_name and item_data["sector"] == "Drink":
                        return True, item_name
        return False, None

    def add_ship(self, ship_data):
        """Add a purchased ship to the fleet and update stats."""
        # Calculate individual ship durability based on price
        ship_data['durability_current'] = ship_data['price']
        ship_data['durability_max'] = ship_data['price']
        ship_data['combat_bonus'] = self.calculate_ship_combat_bonus(ship_data)

        self.fleet.append(ship_data)

        if not self.current_ship:
            self.current_ship = ship_data['name']

        self.update_fleet_stats()

    def calculate_ship_combat_bonus(self, ship_data):
        """Calculate combat bonus for individual ship."""
        return (ship_data.get('base_speed', 1) *
                ship_data.get('capacity', 1) *
                ship_data.get('sails_multiplier', 1))

    def update_fleet_stats(self):
        """Calculate combined stats from all ships in fleet with new durability formula."""
        if not self.fleet:
            self.durability_current = 100
            self.durability_max = 100
            self.combat_power = 10
            self.speed = 0
            self.capacity = 0
            return

        # NEW DURABILITY FORMULA: combined fleet price * storage bonus * fleet count
        total_fleet_price = sum(ship.get('price', 0) for ship in self.fleet)

        # Calculate storage item capacity bonus
        storage_bonus = 1.0
        for item_name, (units, _) in self.portfolio.items():
            for item in items:
                if item['name'] == item_name and item['sector'] == 'Storage':
                    effect_avg = sum(item.get('effect', (1, 1))) / 2
                    storage_bonus += (effect_avg * units * 0.01)  # 1% per unit

        # Apply durability formula
        fleet_count = len(self.fleet)
        self.durability_max = int(total_fleet_price * storage_bonus * max(1, fleet_count * 0.5))
        self.durability_current = min(self.durability_current, self.durability_max)

        # Calculate combat power - NEW FORMULA
        total_fleet_capacity = sum(ship.get('capacity', 0) for ship in self.fleet)

        # Calculate combat item bonus
        combat_item_bonus = 0
        for item_name, (units, _) in self.portfolio.items():
            for item in items:
                if item['name'] == item_name and item['sector'] == 'Combat':
                    effect_sum = sum(item.get('effect', (1, 1)))
                    combat_item_bonus += (effect_sum * units * 0.01)  # 1% per effect point

        # COMBAT POWER FORMULA: base_combat * total_capacity * (1 + combat_bonus)
        base_combat = 10
        self.combat_power = int(base_combat * total_fleet_capacity * (1 + combat_item_bonus))

        # Update speed and capacity
        total_base_speed = sum(ship.get('base_speed', 1) for ship in self.fleet)
        self.speed = total_base_speed * self.sails
        self.capacity = total_fleet_capacity

    def repair_all_ships(self):
        """Repair all ships in fleet to full durability and update player stats."""
        if not self.fleet:
            return False

        # Repair each individual ship
        for ship in self.fleet:
            ship['durability_current'] = ship['durability_max']

        # Update player's combined durability
        self.update_fleet_stats()
        return True

    def calculate_repair_cost(self):
        """Calculate total repair cost for entire fleet."""
        if not self.fleet:
            return 0

        total_missing_durability = 0
        for ship in self.fleet:
            current = ship.get('durability_current', ship.get('durability_max', 0))
            max_dura = ship.get('durability_max', 0)
            total_missing_durability += (max_dura - current)

        # Cost is 1% of missing durability value
        return total_missing_durability * 0.01

    def get_fleet_durability_percentage(self):
        """Get current fleet durability as percentage."""
        if not self.fleet or self.durability_max <= 0:
            return 0

        return (self.durability_current / self.durability_max) * 100

    def calculate_ship_combat_power(self, ship_data):
        """Calculate individual ship combat power based on its stats"""
        base_combat = (ship_data.get('base_speed', 1) * 10 +
                       ship_data.get('capacity', 1) * 2 +
                       ship_data.get('price', 0) / 10)
        return max(1, base_combat)

    def update_fleet_stats(self):
        """Calculate combined stats from all ships in fleet."""

        if not self.fleet:
            self.base_ship_speed = 0
            self.durability_current = []
            self.current_ship = None
            self.durability_max = []
            self.combat_power = 10
            self.speed = 0
            self._speed = 1
            self.capacity = 0
            return

        # Sum durability from all ships
        total_current_durability = sum(ship.get('durability_current', 0) for ship in self.fleet)
        total_max_durability = sum(ship.get('durability_max', 0) for ship in self.fleet)

        # Sum other stats
        total_base_speed = sum(ship.get('base_speed', 1) for ship in self.fleet)
        total_capacity = sum(ship.get('capacity', 0) for ship in self.fleet)
        total_combat = sum(ship.get('combat_bonus', 0) for ship in self.fleet)

        self.durability_current = total_current_durability
        self.durability_max = total_max_durability
        self.combat_power = 10 + total_combat
        self.speed = total_base_speed * self.sails
        self.capacity = total_capacity

        # Apply item effects
        self.recalc_ship_speed()
        self.recalc_ship_capacity()

    def recalc_ship_speed(self):
        """Recalculate final sailing speed based on ALL ships and navigation items."""
        if not self.fleet:
            self._speed = 1
            return self._speed

        # Start with total fleet base speed
        fleet_base_speed = sum(ship.get('base_speed', 1) for ship in self.fleet)
        final_speed = fleet_base_speed
        self._speed = min(final_speed, self.max_speed)

        # --- Navigation Tools: additive percentage bonus ---
        nav_bonus = 0.0
        for item_name in self.navigation_items:
            if any(word in item_name for word in ["Compass", "Astrolabe", "Map", "Sextant"]):
                for entry in items:
                    if entry["name"] == item_name:
                        effect = random.uniform(*entry["effect"]) / 100  # convert to percent
                        nav_bonus += effect
                        break

        # --- Sails: multiplicative bonus ---
        sail_multiplier = 1.0
        sail_items = [item for item in self.navigation_items if "Sail" in item]

        for item_name in sail_items:
            for entry in items:
                if entry["name"] == item_name:
                    # Sail effects are multipliers (e.g., 1.1 for 10% boost)
                    sail_effect = random.uniform(*entry["effect"])
                    sail_multiplier *= sail_effect
                    break

        # Base fleet speed × sail multiplier × (1 + navigation bonus)
        final_speed = final_speed * sail_multiplier * (1 + nav_bonus)

        # Clamp to max speed
        self._speed = min(final_speed, self.max_speed)

        print(
            f"DEBUG SPEED: Fleet={fleet_base_speed}, Sails×{sail_multiplier:.2f}, Nav+{nav_bonus:.2f} = {self._speed:.1f}")
        return self._speed

    def recalc_ship_capacity(self):
        """Recalculate ship capacity including storage items."""
        if not self.fleet:
            self.capacity = 1
            return self.capacity

        # Start with total fleet capacity
        fleet_capacity = sum(ship.get('capacity', 0) for ship in self.fleet)
        final_capacity = fleet_capacity

        # Add storage bonuses from items in portfolio
        storage_bonus = 0
        for item_name, (units, cost) in self.portfolio.items():
            # Look for storage items
            for item_data in items:
                if item_data["name"] == item_name and item_data.get("sector") == "Storage" and units > 0:
                    # Add the effect range average as bonus per share
                    min_eff, max_eff = item_data["effect"]
                    storage_bonus += (min_eff + max_eff) / 2 * units
                    break

        self.capacity = final_capacity + storage_bonus
        return self.capacity

    def update_ship_stats(self, ship_data):
        """Apply ship bonuses and item effects."""
        self.base_ship_speed = ship_data.get('base_speed', 1)
        self.ship_capacity = ship_data.get('capacity', 0)
        self.combat_power = ship_data.get('combat', 0)

        # Update the player's actual speed and capacity
        self._speed = self.base_ship_speed
        self.capacity = self.ship_capacity

        # Recalculate with navigation items and sails
        self.recalc_ship_speed()

        # Also recalculate capacity based on storage items
        self.recalc_ship_capacity()

    @property
    def speed(self):
        """Get the actual speed (minimum of player-controlled speed and calculated max)."""
        if not self.fleet:
            return self._current_speed

        # Calculate maximum possible speed based on fleet
        base_speed = sum(ship.get('base_speed', 1) for ship in self.fleet)
        sails_multiplier = sum(ship.get('sails_multiplier', 1) for ship in self.fleet) / len(self.fleet)
        durability_penalty = self.durability_current / self.durability_max

        max_possible_speed = 2 + base_speed * sails_multiplier * durability_penalty + self.dehydration_awareness

        # Return the lower of player-controlled speed or max possible
        return min(self._current_speed, max_possible_speed)

    @speed.setter
    def speed(self, value):
        """Allow player to set their desired speed."""
        self._current_speed = max(0, value)  # Ensure speed is never negative

    @property
    def max_speed(self):
        """Calculate dynamic maximum possible speed based on fleet composition."""
        if not self.fleet:
            return self._current_speed or 0

        # Find the fastest ship's base speed
        fastest_ship_speed = max(ship.get('base_speed', 1) for ship in self.fleet)

        # Optional: consider sails multiplier if ships have one
        avg_sail_multiplier = (
                sum(ship.get('sails_multiplier', 1) for ship in self.fleet) / 1.1
        )

        # Dynamic max speed = 5 × fastest base × sail factor
        return fastest_ship_speed * avg_sail_multiplier * 5