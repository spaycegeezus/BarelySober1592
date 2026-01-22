# this is database.py
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ITEM_DB_PATH = os.path.join(BASE_DIR, "game_data", "item_market.db")
SHIP_DB_PATH = os.path.join(BASE_DIR, "game_data", "ship_market.db")

enemy_vessels_data = [
    ("Galleon", 200000, 11.0, 150, 2.5, "enemy_galleon.png"),
    ("Frigate", 500000, 15.0, 220, 3.0, "enemy_frigate.png"),
    ("Caravel",  22000, 7.2, 28, 1.4,"enemy_caravel.png"),
    ("Pirate Brig", 15000, 7.5, 25, 1.2, "enemy_brig.png"),
    ("Naval Frigate", 500000, 15.0, 220, 3.0, "enemy_naval_frigate.png"),
    ("Smuggler Sloop", 5000, 5.8, 6, 1.2, "enemy_sloop.png"),
    ("Black Sail Pirates", 150000, 14.0, 140, 2.2, "enemy_black_sail.png"),
    ("Marauder Schooner", 7500, 6.0, 10, 1.8, "cursed_schooner_ship.png"),
    ("Cast Away Carrack", 30000, 9.0, 60, 1.4, "enemy_carrack.png"),
    ("Ghost Ship", 75000, 12.0, 100, 1.8, "enemy_ghost_ship.png"),
    ("Marauder Sloop", 8000, 6.2, 5, 1.4, "cursed_sloop_ship.png"),
]


# Format: (Name, Cost, Speed, Crew, Sail Multiplier, PNG)
ships = [
    # ------------------------
    # Small Ships / Starter Tier
    # ------------------------
    ("Rowboat", 1000, 4.0, 4, 1.0, "rowboat.png"),
    ("Fishing Skiff", 1500, 6, 2, 1.0, "fishing_skiff.png"),
    ("Dinghy", 2000, 4.8, 4, 1.1, "dinghy.png"),
    ("Cutter", 3000, 5.5, 5, 1.2, "cutter.png"),
    ("Sloop", 5000, 5.8, 6, 1.2, "sloop.png"),
    ("Merchant Schooner", 7500, 6.0, 10, 1.8, "merchant_schooner.png"),
    ("Cursed Dinghy", 8000, 6.2, 5, 1.4, "cursed_dinghy.png"),

    # ------------------------
    # Mid-Tier Ships
    # ------------------------
    ("Brigantine", 15000, 7.5, 25, 1.2, "brigantine.png"),
    ("Barque", 18000, 7.0, 30, 1.3, "barque.png"),
    ("Caravel", 22000, 7.2, 28, 1.4, "caravel.png"),
    ("Man O' War", 30000, 9.0, 60, 1.4, "man_o_war.png"),
    ("Ghost Frigate", 75000, 12.0, 100, 1.8, "ghost_frigate.png"),
    ("Clipper Ship", 120000, 13.5, 120, 2.0, "clipper_ship.png"),
    ("Corsair Raider", 150000, 14.0, 140, 2.2, "corsair_raider.png"),

    # ------------------------
    # Large / Advanced Ships
    # ------------------------
    ("Galleon", 200000, 11.0, 150, 2.5, "galleon.png"),
    ("Royal Frigate", 500000, 15.0, 220, 3.0, "royal_frigate.png"),
    ("Dragon Ship", 750000, 16.0, 250, 3.5, "dragon_ship.png"),
    ("Sea Serpent", 1000000, 17.5, 300, 4.0, "sea_serpent.png"),
    ("Leviathan", 1500000, 18.0, 350, 4.5, "leviathan.png"),

    # ------------------------
    # Extreme / Legendary Ships
    # ------------------------
    ("Flying Dutchman", 2500000, 20.0, 400, 5.0, "flying_dutchman.png"),
    ("Kraken Maw", 3000000, 19.5, 380, 5.2, "kraken_maw.png"),
    ("Phoenix Galleon", 3500000, 21.0, 420, 5.5, "phoenix_galleon.png"),
    ("Tempest Clipper", 4000000, 22.5, 450, 5.8, "tempest_clipper.png"),
    ("Celestial Caravel", 5000000, 23.0, 500, 6.0, "celestial_caravel.png"),
    ("Dread Leviathan", 6000000, 24.0, 550, 6.5, "dread_leviathan.png"),
    ("Aurora Frigate", 7000000, 25.0, 600, 7.0, "aurora_frigate.png"),
    ("Stormbreaker", 10000000, 27.0, 650, 8.0, "stormbreaker_print.png"),
]


#item data
items = [
    # ------------------------
    # TREASURE
    # ------------------------
    {"name": "Gold Bar", "sector": "Treasure", "price": 500, "effect": (1.1, 1.2), "png": "gold_bar.png", "description": "Heavy bar of Gold, Weight is wealth."},
    {"name": "Bag of Gold", "sector": "Treasure", "price": 120, "effect": (3.5, 7.0), "png": "bag_gold.png", "description": "A small bag of gold coins. Boosts wealth by 3-7%."},
    {"name": "Gold Coins", "sector": "Treasure", "price": 200, "effect": (4.0, 8.0), "png": "gold_coins.png", "description": "Loose gold coins. Increases wealth by 4-8%."},
    {"name": "Gold Treasure Chest", "sector": "Treasure", "price": 500, "effect": (6.0, 10.0), "png": "gold_treasure_chest.png", "description": "A heavy chest of gold and jewels. Boosts wealth by 6-10%."},
    {"name": "Jeweled Goblet", "sector": "Treasure", "price": 350, "effect": (5.0, 9.0), "png": "jeweled_goblet.png", "description": "A goblet encrusted with gems. Increases prestige and wealth slightly."},
    {"name": "Pirate’s Booty", "sector": "Treasure", "price": 650, "effect": (7.0, 12.0), "png": "pirates_booty.png", "description": "A mix of gold, gems, and stolen trinkets. Wealth boost 7-12%."},

    # ------------------------
    # NAVIGATION
    # ------------------------
    {"name": "Cheap Compass", "sector": "Navigation", "price": 12, "effect": (1.7, 2.5), "png": "cheap_compass.png", "description": "A basic compass. Improves navigation by 1.7-2.5%."},
    {"name": "Basic Compass", "sector": "Navigation", "price": 12, "effect": (2.7, 5.5), "png": "compass.png", "description": "A basic compass. Improves navigation by 2.5-5.5%."},
    {"name": "Brass Compass", "sector": "Navigation", "price": 75, "effect": (4.0, 7.5), "png": "brass_compass.png", "description": "A sturdy brass compass. Navigation +4-7.5%."},
    {"name": "Magic Compass", "sector": "Navigation", "price": 500, "effect": (30.0, 40.0), "png": "magic_compass.png", "description": "Mystical compass that always points to your goal. +30-40% bonus"},

    {"name": "Astrolabe", "sector": "Navigation", "price": 150, "effect": (6.0, 10.0), "png": "astrolabe.png", "description": "Ancient astronomical tool. Navigation +6-10%."},
    {"name": "Sextant", "sector": "Navigation", "price": 200, "effect": (7.0, 12.0), "png": "sextant.png", "description": "Precision instrument for plotting stars. Navigation +7-12%."},

    {"name": "Navigator’s Map", "sector": "Navigation", "price": 300, "effect": (8.0, 15.0), "png": "navigators_map.png", "description": "Detailed map of dangerous waters. Navigation +8-15%."},
    {"name": "Ancient Map", "sector": "Navigation", "price": 150, "effect": (22.0, 27.0), "png": "ancient_map.png", "description": "Faded map showing hidden islands and secret coves."},


    # ------------------------
    # SAILS
    # ------------------------
    {"name": "Silk Sail", "sector": "Navigation", "price": 1800, "effect": (4.2, 4.9), "png": "silk_sail.png", "description": "Finely woven sails that can increase the speed of a vessel. 120%-190%"},
    {"name": "Cotton Sail", "sector": "Navigation", "price": 1300, "effect": (2.0, 3.0), "png": "cotton_sail.png", "description": "Hand woven sails that can increase the speed of a vessel. 200%-300%"},
    {"name": "Linen Sail", "sector": "Navigation", "price": 1500, "effect": (3.0, 4.0), "png": "linen_sail.png", "description": "Loom woven sails that can increase the speed of a vessel. 300%-400%"},

    # ------------------------
    # LIGHTING
    # ------------------------
    {"name": "Candle", "sector": "Lighting", "price": 50, "effect": (2.1, 2.5), "png": "candle.png", "description": "Basic candle for ship lighting. +2-3% visibility."},
    {"name": "Lantern", "sector": "Lighting", "price": 150, "effect": (4.1, 5.5), "png": "lantern.png", "description": "Basic lantern for ship lighting. +4.1-5.5% visibility."},

    # ------------------------
    # COMBAT
    # ------------------------
    {"name": "Dull Dagger", "sector": "Combat", "price": 25, "effect": (1.5, 3.0), "png": "dull_dagger.png", "description": "A weathered dagger, nicked from countless scraps in taverns. Not very sharp, but better than bare hands."},
    {"name": "Dagger", "sector": "Combat", "price": 45, "effect": (3.0, 5.0), "png": "dagger.png", "description": "A well-balanced blade, perfect for quick strikes. Many sailors carry it hidden in boots or belts."},
    {"name": "Rusty Dagger", "sector": "Combat", "price": 60, "effect": (2, 5), "png": "rusty_dagger.png", "description": "Neglected dagger, quick but unreliable."},
    {"name": "Iron Dagger", "sector": "Combat", "price": 38, "effect": (2.2, 4.0), "png": "iron_dagger.png", "description": "Forged from simple iron. Heavy and reliable, often used for boarding small vessels."},
    {"name": "Silver Dagger", "sector": "Combat", "price": 90, "effect": (3.5, 6.0), "png": "silver_dagger.png", "description": "A gleaming silver dagger, rumored to be blessed against curses and foul spirits."},
    {"name": "Jeweled Dagger", "sector": "Combat", "price": 200, "effect": (5.0, 8.0), "png": "jeweled_dagger.png", "description": "Embedded with sapphires and rubies, this dagger is as much a treasure as a weapon."},

    # ------------------------
    # CANNON AMMUNITION TYPES
    # ------------------------
    {"name": "Round Shot", "sector": "Combat", "price": 15, "effect": (8.0, 12.0), "png": "canon_shot_round.png", "description": "Standard solid cannonball. Reliable hull-breaker that punches through enemy ships. The workhorse of naval warfare."},
    {"name": "Chain Shot", "sector": "Combat", "price": 25, "effect": (5.0, 15.0), "png": "canon_shot_chain.png", "description": "Two cannonballs linked by chain. Devastating against sails and rigging. Leaves enemy ships dead in the water."},
    {"name": "Grape Shot", "sector": "Combat", "price": 20, "effect": (3.0, 18.0), "png": "canon_shot_grape.png", "description": "Cluster of small metal balls. Anti-personnel round that clears enemy decks. Perfect for boarding actions."},
    {"name": "Bar Shot", "sector": "Combat", "price": 30, "effect": (6.0, 14.0), "png": "canon_shot_bar.png", "description": "Solid iron bar that tumbles through the air. Creates massive holes in sails and shreds rigging with brutal efficiency."},
    {"name": "Fuse Shot", "sector": "Combat", "price": 40, "effect": (10.0, 25.0), "png": "canon_shot_fuse.png", "description": "Hollow shot filled with gunpowder and timed fuse. Explodes inside enemy hulls. High risk, high reward."},

    {"name": "Cracked Canon", "sector": "Combat", "price": 200, "effect": (4.0, 7.0), "png": "cracked_canon.png", "description": "An old ship canon, its barrel cracked from overuse. Fires with a dangerous unpredictability, favored by desperate captains."},
    {"name": "12 Pound Canon", "sector": "Combat", "price": 300, "effect": (15, 25), "png": "12_pound_canon.png", "description": "Heavy canon capable of blasting hulls wide open."},
    {"name": "canon Royal", "sector": "Combat", "price": 400, "effect": (20, 35), "png": "canon_royal.png", "description": "Majestic canon fit for royal decks."},
    {"name": "Canon", "sector": "Combat", "price": 300, "effect": (6.0, 10.0), "png": "canon.png", "description": "A sturdy ship-mounted canon, capable of blasting enemy hulls with deadly precision."},
    {"name": "Robinet Canon", "sector": "Combat", "price": 320, "effect": (15, 28), "png": "robinet_canon.png", "description": "Compact canon, quick to reload."},
    {"name": "Culverin Canon", "sector": "Combat", "price": 350, "effect": (18, 30), "png": "culverin_canon.png", "description": "Long-range canon with precision fire."},
    {"name": "Murderer Canon", "sector": "Combat", "price": 450, "effect": (22, 38), "png": "murderer_canon.png", "description": "Deadly canon known for its accuracy and destruction."},
    {"name": "Saker Canon", "sector": "Combat", "price": 400, "effect": (18, 32), "png": "saker_canon.png", "description": "Medium-range canon, versatile and dependable."},

    {"name": "Sword", "sector": "Combat", "price": 80, "effect": (4.5, 6.5), "png": "sword.png", "description": "A reliable cutlass, slightly curved and polished. Standard issue for deckhands who know their way around a fight."},
    {"name": "Dull Sword", "sector": "Combat", "price": 40, "effect": (2.5, 3.5), "png": "dull_sword.png", "description": "A cutlass that has seen better days. Rusted and blunt, yet still capable of fending off small threats."},
    {"name": "Rusty Sword", "sector": "Combat", "price": 70, "effect": (3, 6), "png": "rusty_sword.png", "description": "Old sword, edges dulled but still usable."},

    {"name": "Rusty Cutlass", "sector": "Combat", "price": 45, "effect": (2.5, 4.2), "png": "rusty_cutlass.png", "description": "A cutlass that’s seen years of neglect. Rusty but still deadly in skilled hands."},
    {"name": "Polished Cutlass", "sector": "Combat", "price": 120, "effect": (4.8, 7.0), "png": "polished_cutlass.png", "description": "Shiny and sharpened, this cutlass gleams in sunlight. Carried by ambitious sailors seeking respect."},
    {"name": "Fancy Cutlass", "sector": "Combat", "price": 200, "effect": (5, 12), "png": "fancy_cutlass.png", "description": "A flashy sword to impress and intimidate."},
    {"name": "Ornate Cutlass", "sector": "Combat", "price": 180, "effect": (5.5, 8.5), "png": "ornate_cutlass.png", "description": "Intricately engraved with flowing patterns. A captain’s pride, both weapon and status symbol."},

    {"name": "Rusty Saber", "sector": "Combat", "price": 60, "effect": (3.0, 5.5), "png": "rusty_saber.png", "description": "Its edge dull with neglect, yet its swing still carries authority. Favored by old deckhands."},
    {"name": "Fancy Saber", "sector": "Combat", "price": 160, "effect": (4.8, 8.0), "png": "fancy_saber.png", "description": "Polished to perfection, often wielded by officers with a taste for flair."},
    {"name": "Ornate Saber", "sector": "Combat", "price": 200, "effect": (5, 12), "png": "ornate_saber.png", "description": "Saber with intricate decorations, perfect for duels."},

    {"name": "Captain’s Saber", "sector": "Combat", "price": 240, "effect": (5.5, 9.2), "png": "captains_saber.png", "description": "Crafted for command. Every swing tells a story of authority and conquest."},
    {"name": "Captain Sword", "sector": "Combat", "price": 250, "effect": (5, 10), "png": "captain_sword.png", "description": "Finely balanced sword, wielded by experienced captains."},

    {"name": "Wooden Club", "sector": "Combat", "price": 25, "effect": (1.8, 3.5), "png": "wooden_club.png", "description": "A simple chunk of wood, swung with brute force. Not elegant, but effective in a brawl."},
    {"name": "Iron Club", "sector": "Combat", "price": 75, "effect": (3.0, 5.8), "png": "iron_club.png", "description": "Reinforced with iron bands. It delivers bone-shattering impacts in close combat."},
    {"name": "Spiked Club", "sector": "Combat", "price": 110, "effect": (4.0, 6.5), "png": "spiked_club.png", "description": "Studded with spikes, this brutal weapon is a favorite among hardened raiders."},

    {"name": "Short Spear", "sector": "Combat", "price": 60, "effect": (2.5, 5.0), "png": "short_spear.png", "description": "Ideal for deck-to-deck skirmishes. Light, fast, and easy to thrust over railings."},
    {"name": "Steel Spear", "sector": "Combat", "price": 130, "effect": (4.0, 7.0), "png": "steel_spear.png", "description": "Made from hardened steel, capable of piercing most armor aboard enemy ships."},
    {"name": "Ornate Spear", "sector": "Combat", "price": 220, "effect": (5.5, 9.0), "png": "ornate_spear.png", "description": "Adorned with engravings of waves and storms. A show of both skill and wealth."},

    {"name": "Battle Axe", "sector": "Combat", "price": 150, "effect": (5.0, 8.0), "png": "battle_axe.png", "description": "A heavy axe for tearing through wooden doors and hulls alike."},
    {"name": "Ornate Axe", "sector": "Combat", "price": 230, "effect": (6.0, 9.5), "png": "ornate_axe.png", "description": "Crafted with decorative etchings. Terrifying in combat, beautiful in the captain’s hall."},
    {"name": "Executioner’s Axe", "sector": "Combat", "price": 280, "effect": (7.0, 10.5), "png": "executioner_axe.png", "description": "Once used for grim justice, now wielded for terrifying effect in shipboard battles."},

    {"name": "Rusty Rapier", "sector": "Combat", "price": 80, "effect": (3.0, 5.8), "png": "rusty_rapier.png", "description": "Thin, pointed, and neglected. Quick thrusts are its only saving grace."},
    {"name": "Silver Rapier", "sector": "Combat", "price": 150, "effect": (4.5, 7.2), "png": "silver_rapier.png", "description": "Elegant and swift, often favored by duelists and swashbucklers alike."},
    {"name": "Royal Rapier", "sector": "Combat", "price": 260, "effect": (6.5, 9.8), "png": "royal_rapier.png", "description": "A blade fit for royalty. Light, deadly, and utterly precise."},

    {"name": "Cracked Pistol", "sector": "Combat", "price": 120, "effect": (4.0, 6.0), "png": "cracked_pistol.png", "description": "An old flintlock pistol, unpredictable but capable of turning the tide of a close fight."},
    {"name": "Flintlock Pistol", "sector": "Combat", "price": 220, "effect": (5.5, 8.5), "png": "flintlock_pistol.png", "description": "Reliable and fast to reload, this pistol has been the downfall of many a rogue sailor."},
    {"name": "Dual Ornate Flintlock Pistols", "sector": "Combat", "price": 1350, "effect": (17.0, 20.0), "png": "dual_ornate_pistols.png", "description": "Adorned with intricate engravings. Its deadly accuracy is matched only by its beauty."},
    {"name": "Flintlock Rifle", "sector": "Combat", "price": 150, "effect": (8, 15), "png": "flintlock_rifle.png", "description": "Reliable rifle, deadly at medium range."},
    {"name": "Long Rifle", "sector": "Combat", "price": 180, "effect": (10, 18), "png": "long_rifle.png", "description": "Long-range firearm for precision shots."},
    {"name": "Blunderbuss", "sector": "Combat", "price": 120, "effect": (4, 7), "png": "blunderbuss.png", "description": "Short-range firearm, devastating at close quarters."},
    {"name": "Ornate Rifle", "sector": "Combat", "price": 220, "effect": (12, 20), "png": "ornate_rifle.png", "description": "Beautifully engraved rifle, functional and elegant."},

    {"name": "Throwing Knife", "sector": "Combat", "price": 40, "effect": (2.0, 4.0), "png": "throwing_knife.png", "description": "Small, balanced, and easy to conceal. Perfect for silent strikes."},
    {"name": "Balanced Knife", "sector": "Combat", "price": 75, "effect": (3.5, 6.0), "png": "balanced_knife.png", "description": "Engineered for perfect flight, hitting its target with deadly precision."},
    {"name": "Assassin’s Knife", "sector": "Combat", "price": 180, "effect": (5.0, 8.5), "png": "assassins_knife.png", "description": "Forged in secrecy and shadowed lore, this blade whispers death to its victim."},

    {"name": "Crude Halberd", "sector": "Combat", "price": 90, "effect": (3.5, 6.5), "png": "crude_halberd.png", "description": "A rough weapon, combining spear and axe. Heavy-handed, but effective against boarding parties."},
    {"name": "Steel Halberd", "sector": "Combat", "price": 170, "effect": (5.0, 8.0), "png": "steel_halberd.png", "description": "Forged for discipline and power, perfect for defending the ship’s deck."},
    {"name": "Royal Halberd", "sector": "Combat", "price": 260, "effect": (6.5, 9.8), "png": "royal_halberd.png", "description": "Decorated with crests and filigree. Imposing, respected, and feared in naval battles."},

    # ------------------------
    # SHIP / STORAGE
    # ------------------------
    {"name": "Small Barrel", "sector": "Storage", "price": 15, "effect": (1.0, 2.0), "png": "small_barrel.png", "description": "Compact wooden barrel. +1-2% storage efficiency."},
    {"name": "Medium Barrel", "sector": "Storage", "price": 25, "effect": (1.5, 3.0), "png": "barrel.png", "description": "Standard wooden barrel. +1.5-3% storage efficiency."},
    {"name": "Large Barrel", "sector": "Storage", "price": 50, "effect": (3.0, 5.0), "png": "large_barrel.png", "description": "Extra-large barrel for bulk goods. +3-5% storage efficiency."},
    {"name": "Barrel of Endless Provisions", "sector": "Storage", "price": 1200, "effect": (12.0, 18.0), "png": "endless_barrel.png", "description": "Magic barrel that replenishes itself. +12-18% storage capacity."},

    {"name": "Crate", "sector": "Storage", "price": 40, "effect": (2.0, 4.0), "png": "crate.png", "description": "Wooden crate for general cargo. +2-4% storage efficiency."},
    {"name": "Sturdy Crate", "sector": "Storage", "price": 70, "effect": (3.0, 6.0), "png": "sturdy_crate.png", "description": "Reinforced crate for heavy goods. +3.5-6% storage efficiency."},
    {"name": "Void Crate", "sector": "Storage", "price": 3000, "effect": (35, 65), "png": "void_crate.png", "description": "A container to a realm of unknown origins that retrieves items on summon. +35-65% storage efficiency, reduces loss chance."},

    {"name": "Rope Coil", "sector": "Storage", "price": 30, "effect": (1.5, 3.5), "png": "rope_coil.png", "description": "Coiled rope for general rigging. Improves ship operations +1.5-3.5%."},
    {"name": "Sturdy Rope", "sector": "Storage", "price": 75, "effect": (2.0, 5.1), "png": "rope.png", "description": "Heavy-duty rope for critical rigging. Improves ship operations +2-5%."},
    {"name": "Enchanted Rope", "sector": "Storage", "price": 200, "effect": (5.0, 9.0), "png": "enchanted_rope.png", "description": "Magically reinforced rope. +5-9% to ship handling and rigging efficiency."},
    {"name": "Reinforced Cargo Net", "sector": "Storage", "price": 150, "effect": (2.5, 5.0), "png": "cargo_net.png", "description": "Strong net to hold supplies on deck. +2.5-5% storage stability."},

    {"name": "Treasure Chest", "sector": "Storage", "price": 500, "effect": (6.0, 10.0), "png": "treasure_chest.png", "description": "Large chest to store treasures. +6-10% storage capacity."},
    {"name": "Mythical Chest of Plenty", "sector": "Storage", "price": 1000, "effect": (10.0, 15.0), "png": "mythical_chest.png", "description": "Chest blessed by a sea god. Greatly increases storage +10-15%."},
    {"name": "Cursed Chest", "sector": "Storage", "price": 750, "effect": (5.0, 8.0), "png": "cursed_chest.png", "description": "A chest imbued with dark magic. +5-8% storage, but may attract sea monsters."},
    {"name": "Mystic Satchel", "sector": "Storage", "price": 8000, "effect": (45, 75), "png": "mystic_satchel.png", "description": "Small bag imbued with magic to hold more than it seems. +45-75% storage efficiency."},

    # ------------------------
    # Food/Drink
    # ------------------------
    {"name": "Rum Bottle", "sector": "Food/Drink", "price": 95, "effect": (3.0, 5.5), "png": "rum_bottle.png", "description": "A potent bottle of rum. Boosts speed +30-55%, but dehydration rises +30-50%. Increases chance of monster encounters."},
    {"name": "Grog", "sector": "Food/Drink", "price": 70, "effect": (2.5, 4.0), "png": "grog.png", "description": "Cheap sailors’ grog. Speed +25-40%, dehydration +25-40%. Controls may drift unpredictably."},
    {"name": "Glass of Wine", "sector": "Food/Drink", "price": 80, "effect": (2.3, 4.9), "png": "glass_wine.png", "description": "Fine wine to steady your nerves. Speed +23-49%, mild dehydration +20-35%. Vision slightly blurred."},
    {"name": "Wine Bottle", "sector": "Food/Drink", "price": 100, "effect": (3.5, 5.9), "png": "grapa_wine.png", "description": "A full bottle of wine. Speed +35-59%, dehydration +30-50%. Slightly increases risk of sea encounters."},
    {"name": "Wine Barrel", "sector": "Food/Drink", "price": 1000, "effect": (6.5, 7.9), "png": "wine_barrel.png", "description": "A full barrel of wine. Speed +65-79%, dehydration +65-79%. Slightly increases risk of sea encounters."},
    {"name": "Beer Barrel", "sector": "Food/Drink", "price": 500, "effect": (6.5, 9.5), "png": "beer_barrel.png", "description": "Foamy beer to boost morale. Speed +15-35%, dehydration +10-25%. Controls may wobble slightly."},
    {"name": "Spiced Rum", "sector": "Food/Drink", "price": 120, "effect": (4.0, 6.5), "png": "spiced_rum.png", "description": "Strong spiced rum. Speed +40-65%, dehydration +40-60%. Vision blurs, and sea monster encounter chance increases."},
    {"name": "Absinthe Shot", "sector": "Food/Drink", "price": 150, "effect": (5.0, 8.0), "png": "absinthe_shot.png", "description": "A dangerously strong absinthe. Speed +50-80%, dehydration +50-70%. Controls wildly erratic, hallucinations possible, monster encounters very likely."},
    {"name": "Mead", "sector": "Food/Drink", "price": 600, "effect": (30.0, 60.0), "png": "mead.png", "description": "Sweet honey mead. Speed +20-40%, dehydration +15-30%. Slight blur of vision, small chance of sea encounter."},

    {"name": "Kraken’s Rum", "sector": "Food/Drink", "price": 3000, "effect": (60.0, 100.0), "png": "kraken_rum.png", "description": "A legendary rum said to awaken the Kraken. Speed +60-100%, dehydration +60-80%. Vision severely blurred, controls chaotic, sea monsters extremely likely!"},
    {"name": "Poseidon’s Elixir", "sector": "Food/Drink", "price": 3500, "effect": (70.0, 100.0), "png": "poseidon_elixir.png", "description": "Brewed by Poseidon himself. Speed +70-110%, dehydration +70-90%. Water currents act strangely, hallucinations, monster and sea god encounters almost guaranteed!"},
    {"name": "Mermaid’s Nectar", "sector": "Food/Drink", "price": 2500, "effect": (50.5, 90.5), "png": "mermaid_nectar.png", "description": "Sweet, shimmering liquid. Speed +55-95%, dehydration +50-70%. Vision sparkles and controls drift, small chance of siren encounter."},
    {"name": "Viking Mead", "sector": "Food/Drink", "price": 1800, "effect": (40.5, 80.0), "png": "viking_mead.png", "description": "Strong Nordic mead. Speed +45-80%, dehydration +40-65%. Hallucinogenic effects, risk of Norse monster attacks."},

    {"name": "Samurai Sake", "sector": "Food/Drink", "price": 2000, "effect": (50.0, 80.0), "png": "samurai_sake.png", "description": "Refined sake from the Far East. Speed +50-85%, dehydration +45-65%. Precision of controls unstable, occasional spectral samurai encounters."},
    {"name": "Aztec Tequila", "sector": "Food/Drink", "price": 1500, "effect": (40.0, 70.0), "png": "aztec_tequila.png", "description": "Ancient tequila infused with mystical agave spirits. Speed +40-75%, dehydration +35-60%. Hallucinations of jaguar spirits, chance of random monster encounters."},
    {"name": "Russian Shaman Vodka", "sector": "Food/Drink", "price": 1400, "effect": (40.0, 70.0), "png": "russian_vodka.png", "description": "Pure, icy vodka. Speed +40-70%, dehydration +35-55%. Extreme control drift, vision blurred, occasional frost giant hallucinations!"},
    {"name": "Caribbean Firewater", "sector": "Food/Drink", "price": 2200, "effect": (50., 90.0), "png": "caribbean_firewater.png", "description": "Fiery spirit from the tropics. Speed +55-90%, dehydration +50-75%. Controls spin unpredictably, chance of sea monster eruption near the ship!"},
    {"name": "Phoenix Whiskey", "sector": "Food/Drink", "price": 3000, "effect": (60.0, 100.0), "png": "phoenix_whiskey.png", "description": "Whiskey imbued with phoenix flames. Speed +65-105%, dehydration +60-85%. Blurs vision, ignites hallucinations, rare chance of fire-elemental encounter!"},
    {"name": "Neptune’s Nectar", "sector": "Food/Drink", "price": 2800, "effect": (60.0, 100.0), "png": "neptune_nectar.png", "description": "Sea god’s personal Drink. Speed +60-100%, dehydration +55-80%. Ship lurches unpredictably, almost guaranteed encounter with water spirits or sea gods."},

    {"name": "Coconut Water", "sector": "Food/Drink", "price": 400, "effect": (50.0, 80.), "png": "coconut_water.png", "description": "Hydrating coconut water. Reduces dehydration 5-10%, speed unaffected. Safe from alcohol-related penalties."},

    {"name": "Fresh Water", "sector": "Food/Drink", "price": 250, "effect": (40.0, 50.0), "png": "fresh_water.png", "description": "Simple water. Dehydration decreases 10-20%, keeps controls stable and vision clear."},

    # ------------------------
    # Food/Drink
    # ------------------------
    {"name": "Fish", "sector": "Food/Drink", "price": 15, "effect": (1.0, 2.5), "png": "fish.png", "description": "Simple fish meal. Restores 1-2% health."},
    {"name": "Bigfin Fish", "sector": "Food/Drink", "price": 25, "effect": (1.5, 3.5), "png": "fish_bigfin.png", "description": "A large, hearty fish. Restores 1.5-3.5% health."},

    {"name": "Hardtack Biscuit", "sector": "Food/Drink", "price": 10, "effect": (1.0, 2.0), "png": "hardtack.png", "description": "Dry, long-lasting biscuit. Restores 1-2% health."},
    {"name": "Stale Bread", "sector": "Food/Drink", "price": 8, "effect": (0.5, 1.5), "png": "stale_bread.png", "description": "Old bread, barely filling. Restores 0.5-1.5% health."},
    {"name": "Fresh Bread Loaf", "sector": "Food/Drink", "price": 18, "effect": (1.5, 3.0), "png": "fresh_bread_loaf.png", "description": "Freshly baked bread. Restores 1.5-3% health."},

    {"name": "Salted Pork", "sector": "Food/Drink", "price": 22, "effect": (2.0, 3.5), "png": "salted_pork.png", "description": "Preserved pork for sailors. Restores 2-3.5% health."},
    {"name": "Cured Ham", "sector": "Food/Drink", "price": 35, "effect": (3.0, 4.5), "png": "cured_ham.png", "description": "Rich cured ham. Restores 3-4.5% health."},
    {"name": "Ornate Boar Roast", "sector": "Food/Drink", "price": 75, "effect": (5.0, 7.5), "png": "ornate_boar_roast.png", "description": "Lavish boar feast. Restores 5-7.5% health."},

    {"name": "Dried Fish", "sector": "Food/Drink", "price": 18, "effect": (1.5, 3.0), "png": "dried_fish.png", "description": "Preserved dried fish. Restores 1.5-3% health."},
    {"name": "Smoked Eel", "sector": "Food/Drink", "price": 28, "effect": (2.5, 4.0), "png": "smoked_eel.png", "description": "Smoky eel delicacy. Restores 2.5-4% health."},
    {"name": "Butter Fried Cod", "sector": "Food/Drink", "price": 40, "effect": (3.5, 5.0), "png": "butter_fried_cod.png", "description": "Cod fried in butter. Restores 3.5-5% health."},

    {"name": "Roasted Chicken", "sector": "Food/Drink", "price": 30, "effect": (3.0, 4.8), "png": "roasted_chicken.png", "description": "Juicy roasted chicken. Restores 3-4.8% health."},
    {"name": "Herbed Goose", "sector": "Food/Drink", "price": 55, "effect": (4.5, 6.5), "png": "herbed_goose.png", "description": "Seasoned goose feast. Restores 4.5-6.5% health."},
    {"name": "Luxurious Swan Feast", "sector": "Food/Drink", "price": 120, "effect": (6.0, 9.0), "png": "luxurious_swan_feast.png", "description": "Exquisite swan banquet. Restores 6-9% health."},

    {"name": "Apple", "sector": "Food/Drink", "price": 1, "effect": (0.8, 1.5), "png": "apple.png", "description": "Fresh apple. Restores 0.8-1.5% health."},
    {"name": "Bushel Apple", "sector": "Food/Drink", "price": 10, "effect": (0.8, 1.7), "png": "bushel_apple.png", "description": "Fresh apples. Restores 0.8-1.7% health."},

    {"name": "Crate of Oranges", "sector": "Food/Drink", "price": 8, "effect": (1.0, 2.0), "png": "crate_oranges.png", "description": "Citrus fruit. Restores 1-2% health."},
    {"name": "Bananas", "sector": "Food/Drink", "price": 10, "effect": (1.0, 2.5), "png": "bananas.png", "description": "Sweet banana. Restores 1-2.5% health."},

    {"name": "Dried Figs", "sector": "Food/Drink", "price": 12, "effect": (1.5, 2.5), "png": "dried_figs.png", "description": "Sun-dried figs. Restores 1.5-2.5% health."},
    {"name": "Grapes", "sector": "Food/Drink", "price": 14, "effect": (1.5, 2.8), "png": "grapes.png", "description": "Fresh grapes. Restores 1.5-2.8% health."},
    {"name": "Luxurious Pomegranate", "sector": "Food/Drink", "price": 25, "effect": (2.5, 4.0), "png": "pomegranate.png", "description": "Rare pomegranate. Restores 2.5-4.5% health."},

    {"name": "Honeycomb", "sector": "Food/Drink", "price": 22, "effect": (2.0, 3.5), "png": "honeycomb.png", "description": "Sweet honeycomb. Restores 2-3.5% health."},
    {"name": "Bowl of Gruel", "sector": "Food/Drink", "price": 10, "effect": (1.0, 2.0), "png": "bowl_gruel.png", "description": "Thin porridge. Restores 1-2% health."},
    {"name": "Steamed Barley", "sector": "Food/Drink", "price": 14, "effect": (1.5, 2.5), "png": "steamed_barley.png", "description": "Nutritious barley. Restores 1.5-2.5% health."},

    {"name": "Cheese Wedge", "sector": "Food/Drink", "price": 20, "effect": (2.0, 3.5), "png": "cheese_wedge.png", "description": "Simple cheese wedge. Restores 2-3.5% health."},
    {"name": "Fancy Brie Wheel", "sector": "Food/Drink", "price": 38, "effect": (3.0, 5.0), "png": "fancy_brie_wheel.png", "description": "Creamy brie cheese. Restores 3-5% health."},
    {"name": "Ornate Cheese Platter", "sector": "Food/Drink", "price": 65, "effect": (4.5, 7.0), "png": "ornate_cheese_platter.png", "description": "Assorted fine cheeses. Restores 4.5-7% health."},

    {"name": "Meat Pie", "sector": "Food/Drink", "price": 25, "effect": (2.5, 4.0), "png": "meat_pie.png", "description": "Savory meat pie. Restores 2.5-4% health."},
    {"name": "Fancy Steak Pie", "sector": "Food/Drink", "price": 40, "effect": (3.5, 5.5), "png": "steak_pie.png", "description": "Hearty steak pie. Restores 3.5-5.5% health."},
    {"name": "Royal Venison Pie", "sector": "Food/Drink", "price": 80, "effect": (5.5, 8.0), "png": "venison_pie.png", "description": "Luxurious venison pie. Restores 5.5-8% health."},

    {"name": "Bowl of Lentils", "sector": "Food/Drink", "price": 16, "effect": (1.8, 3.0), "png": "bowl_lentils.png", "description": "Hearty lentil stew. Restores 1.8-3% health."},
    {"name": "Spiced Stew", "sector": "Food/Drink", "price": 28, "effect": (2.8, 4.2), "png": "spiced_stew.png", "description": "Warm stew with spices. Restores 2.8-4.2% health."},
    {"name": "Fancy Lobster Stew", "sector": "Food/Drink", "price": 75, "effect": (5.0, 7.5), "png": "fancy_lobster_stew.png", "description": "Deluxe lobster stew. Restores 5-7.5% health."},

]

# Instant Loss Locations
instant_loss_locations = {
    "Bermuda Triangle": {
        "description": "Lost at sea in the mysterious Bermuda Triangle. GAME OVER!",
        "lat": 25.0000,
        "lon": -71.0000
    },
    "Maelstrom of Moskstraumen": {
        "description": "Your ship was sucked into the legendary whirlpool off Norway’s coast.",
        "lat": 68.2000,
        "lon": 14.7000
    },
    "Cape Horn Shipwreck Alley": {
        "description": "Furious winds and waves shattered your ship near Cape Horn.",
        "lat": -56.0000,
        "lon": -67.0000
    },
    "Sargasso Sea Drift": {
        "description": "Your ship was trapped in endless seaweed and died in still waters.",
        "lat": 31.0000,
        "lon": -38.0000
    },
    "Devil’s Sea (Dragon’s Triangle)": {
        "description": "Lost forever in the Devil’s Sea near Japan. No survivors.",
        "lat": 30.0000,
        "lon": 145.0000
    },
    "Skeleton Coast": {
        "description": "Fog and sand claimed your ship off Namibia’s deadly coast.",
        "lat": -19.2000,
        "lon": 12.3000
    },
    "Cape of Good Hope Stormfront": {
        "description": "Rogue waves consumed your vessel near the Cape of Good Hope.",
        "lat": -34.3568,
        "lon": 18.4740
    },
    "Typhoon Trench": {
        "description": "A typhoon ripped your sails apart in the western Pacific. GAME OVER.",
        "lat": 20.0000,
        "lon": 135.0000
    },
    "Titanic Graveyard": {
        "description": "You hit an iceberg drifting near the site of the Titanic wreck.",
        "lat": 41.7325,
        "lon": -49.9469
    },
    "Black Sea Whirlpool": {
        "description": "A massive vortex opened under your ship. The sea swallows you whole.",
        "lat": 43.0000,
        "lon": 35.0000
    },
    "Gulf of Aden Pirate Trap": {
        "description": "Captured and sunk by pirates off the Horn of Africa.",
        "lat": 12.0000,
        "lon": 45.0000
    },
    "Frozen Passage": {
        "description": "Trapped in sea ice, your crew froze before rescue could arrive.",
        "lat": 74.0000,
        "lon": -94.0000
    },
    "Kraken’s Reach": {
        "description": "A monstrous tentacle rises from the deep. Your ship is gone.",
        "lat": 63.0000,
        "lon": -30.0000
    },
    "Lost City of Atlantis": {
        "description": "Your ship vanished beneath strange glowing waters.",
        "lat": 31.0000,
        "lon": -28.0000
    },
    "Sunda Strait Eruption": {
        "description": "A sudden volcanic blast from Krakatoa ends your voyage.",
        "lat": -6.1020,
        "lon": 105.4230
    },
    "Caribbean Reef Trap": {
        "description": "You struck coral and sank among the reefs. The sea reclaims another.",
        "lat": 18.4000,
        "lon": -77.0000
    },
    "Bay of Bengal Cyclone": {
        "description": "A super-cyclone devours your ship and crew. GAME OVER.",
        "lat": 16.0000,
        "lon": 89.0000
    },
    "Drake Passage Fury": {
        "description": "Winds stronger than canon fire splinter your ship south of Chile.",
        "lat": -58.0000,
        "lon": -65.0000
    },
    "North Sea Storm Line": {
        "description": "Caught in a sudden squall; the ship capsizes in icy waters.",
        "lat": 58.0000,
        "lon": 2.0000
    },
    "Whirlpool of Charybdis": {
        "description": "Ancient myth becomes real — your ship is swallowed by Charybdis.",
        "lat": 37.9715,
        "lon": 15.6394
    }
}

# Secret Locations with Special Excursions
secret_locations = {
    "Fountain of Youth": {
        "description": "You wander deep into the jungle. Eternal life has a price! Prepare to survive.",
        "lat": 30.5590,
        "lon": -80.6999
    },
    "Canary Island": {
        "description": "A vibrant port filled with traders and strange fruits. Rumors of a hidden cave of gold!",
        "lat": 28.3000,
        "lon": -15.4000
    },
    "Monkey Island": {
        "description": "A cheeky tribe of monkeys stole your compass. You’ll have to earn it back.",
        "lat": 10.2500,
        "lon": -84.8500
    },
    "Banana Island": {
        "description": "A paradise of endless bananas... but beware the slippery ground and the dancing parrots!",
        "lat": 8.0800,
        "lon": -13.3000
    },
    "Atlantis Ruins": {
        "description": "The sea parts to reveal glowing ruins beneath the waves. Will you dive or flee?",
        "lat": 31.0000,
        "lon": -28.0000
    },
    "Sirens’ Reef": {
        "description": "The haunting songs of sirens echo across the waves. Can you resist their call?",
        "lat": 36.5000,
        "lon": 15.0000
    },
    "Isle of Krakens": {
        "description": "Tentacles breach the surface as the sea trembles... only the brave (or drunk) survive here.",
        "lat": 63.0000,
        "lon": -30.0000
    },
    "El Dorado Coast": {
        "description": "Golden sands shimmer on the horizon. Is this the mythical city of gold?",
        "lat": 4.2000,
        "lon": -74.0000
    },
    "Rumrunner’s Cove": {
        "description": "A hidden cove where smugglers trade barrels of forbidden spirits. Choose wisely, sailor.",
        "lat": 23.0000,
        "lon": -82.0000
    },
    "Dead Man’s Chest Isle": {
        "description": "Fifteen men on a dead man’s chest, yo ho ho and a bottle of rum!",
        "lat": 18.0000,
        "lon": -65.0000
    },
    "Mermaid Lagoon": {
        "description": "You glimpse shimmering scales in the moonlight. The sea itself seems alive.",
        "lat": -20.0000,
        "lon": 160.0000
    },
    "Ship of the Damned": {
        "description": "A ghostly galleon drifts through the mist. Dare to board it?",
        "lat": 47.0000,
        "lon": -7.0000
    },
    "Coconut Lagoon": {
        "description": "Drinks flow freely here. The local spirit may be literal — and mischievous.",
        "lat": -18.0000,
        "lon": 178.0000
    },
    "Pirate King’s Grave": {
        "description": "A lone cross juts from the sand. Dig if you dare — the Pirate King guards his treasure.",
        "lat": 12.0000,
        "lon": -61.0000
    },
    "Skull Island":{
        "description": "Large Kaiju roam the mysterious island with extremely risky temptations for large rewards.",
        "lat": 16.6969,
        "lon": 66.6969
    },
    "Isle of Giants": {
        "description": "Massive footprints and bones line the beach. Something huge once lived here.",
        "lat": -35.0000,
        "lon": 155.0000
    },
    "Whispering Shoals": {
        "description": "The waves whisper secrets of lost voyages. Listen close or lose your mind.",
        "lat": 52.0000,
        "lon": -5.0000
    },
    "Crystal Cove": {
        "description": "Glimmering crystals light the water. It’s beautiful... and deeply unsettling.",
        "lat": -14.0000,
        "lon": -173.0000
    },
    "Frostbite Fjord": {
        "description": "The cold burns your skin, but ancient runes glimmer under the ice.",
        "lat": 72.0000,
        "lon": 28.0000
    },
    "Fire Island": {
        "description": "Volcanoes roar and lava flows into the sea. A place for forging — or dying.",
        "lat": -7.9300,
        "lon": 112.9500
    },
    "Isle of Time": {
        "description": "Your compass spins wildly... time itself bends here. You may leave older or younger.",
        "lat": 45.0000,
        "lon": -30.0000
    },
    "Leviathan’s Lair": {
        "description": "A vast shadow moves beneath the surface — the Leviathan wakes.",
        "lat": -22.0000,
        "lon": 145.0000
    },
    "Ghost Harbor": {
        "description": "Spectral lanterns flicker where no ships should be. The dead still trade here.",
        "lat": 40.0000,
        "lon": -60.0000
    },
    "Whiskey Shoal": {
        "description": "A merchant shipwreck has turned this reef into a whiskey fountain. Don’t drink too deep!",
        "lat": 25.3000,
        "lon": -79.1000
    },
    "Zephyr Isle": {
        "description": "An island of perpetual breeze and songbirds — the calm before every storm.",
        "lat": -10.0000,
        "lon": 150.0000
    }
}

# database.py - Expanded Excursions with Fantasy & Natural Events
excursions = {
    # === NATURAL EVENTS ===
    "Island Raid": {
        "success_rate": 80,
        "reward": 2000,
        "sector": "Food/Drink",
        "dehydration_cost": (2, 4),
        "description": "Raid a tropical island for fresh fruit and supplies."
    },
    "Fresh Water Island": {
        "success_rate": 95,
        "reward": 900,
        "sector": "Hydration",
        "dehydration_cost": (1, 2),
        "description": "Discover a hidden freshwater spring to replenish supplies."
    },
    "Monkey Island": {
        "success_rate": 5,
        "reward": 4500,
        "sector": "Food/Drink",
        "dehydration_cost": (3, 6),
        "description": "Trade with mischievous monkeys for exotic fruits."
    },
    "Banana Island": {
        "success_rate": 70,
        "reward": 6000,
        "sector": "Food/Drink",
        "dehydration_cost": (2, 5),
        "description": "Harvest massive banana groves under the hot sun."
    },

    # === FANTASY ENCOUNTERS ===
    "Siren Song": {
        "success_rate": 70,
        "reward": 25000,
        "sector": "Navigation",
        "dehydration_cost": (10, 15),
        "description": "Resist the hypnotic songs of sirens to claim their treasures.",
        "special_effect": "20% bonus effect to Navigation sector"
    },
    "Kraken's Lair": {
        "success_rate": 40,
        "reward": 120000,
        "sector": "Combat",
        "dehydration_cost": (12, 18),
        "description": "Battle the legendary kraken for its sunken treasure hoard.",
        "special_effect": "Massive gold reward but high dehydration risk"
    },
    "Mermaid Cove": {
        "success_rate": 75,
        "reward": 35000,
        "sector": "Navigation",
        "dehydration_cost": (8, 13),
        "description": "Trade with mermaids for magical navigation aids.",
        "special_effect": "Guaranteed navigation item drop"
    },
    "Ghost Ship Plunder": {
        "success_rate": 45,
        "reward": 80000,
        "sector": "Combat",
        "dehydration_cost": (10, 16),
        "description": "Board a phantom vessel haunted by undead pirates.",
        "special_effect": "Chance to gain cursed artifacts"
    },
    "Dragon Turtle Nest": {
        "success_rate": 35,
        "reward": 150000,
        "sector": "Combat",
        "dehydration_cost": (15, 20),
        "description": "Steal precious gems from a sleeping dragon turtle's nest.",
        "special_effect": "Extreme reward with very high dehydration"
    },

    # === RESOURCE GATHERING ===
    "Pearl Diving": {
        "success_rate": 65,
        "reward": 40000,
        "sector": "Treasure",
        "dehydration_cost": (7, 12),
        "description": "Dive for precious pearls in crystal-clear lagoons."
    },
    "Whale Hunting": {
        "success_rate": 55,
        "reward": 55000,
        "sector": "Food/Drink",
        "dehydration_cost": (9, 14),
        "description": "Hunt majestic whales for oil and meat supplies."
    },
    "Spice Islands": {
        "success_rate": 60,
        "reward": 70000,
        "sector": "Treasure",
        "dehydration_cost": (6, 11),
        "description": "Harvest rare spices from volcanic islands."
    },
    "Coral Reef Fishing": {
        "success_rate": 80,
        "reward": 25000,
        "sector": "Food/Drink",
        "dehydration_cost": (4, 9),
        "description": "Fish in vibrant coral reefs teeming with life."
    },

    # === TREACHEROUS WATERS ===
    "Bermuda Triangle": {
        "success_rate": 30,
        "reward": 200000,
        "sector": "Navigation",
        "dehydration_cost": (20, 25),
        "description": "Navigate the mysterious triangle where ships vanish.",
        "special_effect": "Either massive reward or instant game over"
    },
    "Hurricane Eye": {
        "success_rate": 50,
        "reward": 60000,
        "sector": "Navigation",
        "dehydration_cost": (12, 17),
        "description": "Sail through a massive hurricane to reach the calm eye.",
        "special_effect": "Navigation items provide double effect"
    },
    "Volcanic Island": {
        "success_rate": 40,
        "reward": 90000,
        "sector": "Combat",
        "dehydration_cost": (11, 16),
        "description": "Mine rare minerals from an active volcanic island.",
        "special_effect": "Chance to find magical fire-resistant items"
    },

    # === MYTHICAL LOCATIONS ===
    "Fountain of Youth": {
        "success_rate": 25,
        "reward": 300000,
        "sector": "Hydration",
        "dehydration_cost": (5, 10),
        "description": "Find the legendary fountain that restores youth.",
        "special_effect": "Resets dehydration awareness to 0 on success"
    },
    "Atlantis Exploration": {
        "success_rate": 20,
        "reward": 500000,
        "sector": "Treasure",
        "dehydration_cost": (18, 23),
        "description": "Explore the sunken city of Atlantis for ancient treasures.",
        "special_effect": "Gain permanent navigation bonus if successful"
    },
    "Poseidon's Temple": {
        "success_rate": 35,
        "reward": 110000,
        "sector": "Navigation",
        "dehydration_cost": (13, 18),
        "description": "Raid the underwater temple of the sea god himself.",
        "special_effect": "Poseidon may bless or curse your voyage"
    },

    # === SOCIAL ENCOUNTERS ===
    "Buccaneer BBQ": {
        "success_rate": 75,
        "reward": 5000,
        "sector": "Food/Drink",
        "dehydration_cost": (4, 8),
        "description": "Attend a pirate feast and make valuable connections."
    },
    "Parrot Island": {
        "success_rate": 460,
        "reward": 7500,
        "sector": "Navigation",
        "dehydration_cost": (2, 5),
        "description": "Train magical parrots that reveal hidden treasures."
    },
    "Tribal Trading": {
        "success_rate": 70,
        "reward": 3500,
        "sector": "Food/Drink",
        "dehydration_cost": (3, 5),
        "description": "Trade with isolated island tribes for exotic goods."
    },

    # === DANGEROUS HUNTS ===
    "Sea Serpent Hunt": {
        "success_rate": 35,
        "reward": 115000,
        "sector": "Combat",
        "dehydration_cost": (14, 19),
        "description": "Hunt a massive sea serpent for its valuable scales.",
        "special_effect": "Gain serpent-scale armor if successful"
    },
    "Giant Squid Capture": {
        "success_rate": 25,
        "reward": 180000,
        "sector": "Combat",
        "dehydration_cost": (16, 21),
        "description": "Capture a legendary giant squid alive.",
        "special_effect": "Royal bounty plus rare ink sacs"
    },
    "Megalodon Encounter": {
        "success_rate": 15,
        "reward": 250000,
        "sector": "Combat",
        "dehydration_cost": (25, 30),
        "description": "Fate decided you must make the prehistoric mega-shark extinct by deadly combat.",
        "special_effect": "Highest combat reward in the game"
    }
}


def init_databases():
    """Initialize both databases separately"""
    os.makedirs(os.path.dirname(ITEM_DB_PATH), exist_ok=True)

    # Initialize Items Database
    conn_items = sqlite3.connect(ITEM_DB_PATH)
    cursor_items = conn_items.cursor()

    cursor_items.execute("""
        CREATE TABLE IF NOT EXISTS items (
            name TEXT PRIMARY KEY,
            sector TEXT,
            price REAL,
            effect_min REAL,
            effect_max REAL,
            png TEXT,
            description TEXT
        )
    """)
    conn_items.commit()
    conn_items.close()

    # Initialize Ships Database
    conn_ships = sqlite3.connect(SHIP_DB_PATH)
    cursor_ships = conn_ships.cursor()
    conn_enemy_ships = sqlite3.connect((SHIP_DB_PATH))
    cursor_enemy_ships = conn_enemy_ships.cursor()

    cursor_ships.execute("""
        CREATE TABLE IF NOT EXISTS ships (
            name TEXT PRIMARY KEY,
            price REAL,
            base_speed REAL,
            capacity INTEGER,
            sails_multiplier REAL,
            png TEXT
        )
    """)

    # Create enemy ships table
    cursor_enemy_ships.execute("""
        CREATE TABLE IF NOT EXISTS enemy_vessels_data (
            name TEXT PRIMARY KEY,
            price REAL,
            base_speed REAL,
            capacity INTEGER,
            sails_multiplier REAL,
            png TEXT
        )
    """)
    conn_ships.commit()
    conn_ships.close()
    conn_enemy_ships.commit()
    conn_enemy_ships.close()

def validate_all_items():
    """Quick fix for all item data issues."""
    global items

def populate_items():
    """Populate the items database"""
    validate_all_items()

    conn = sqlite3.connect("game_data/item_market.db")
    c = conn.cursor()

    # Insert all items
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
    print(f"✅ {len(items)} items populated successfully!")

def populate_ships():
    """Populate the ships database with both player and enemy ships"""
    conn = sqlite3.connect(SHIP_DB_PATH)
    c = conn.cursor()

    # Insert player ships
    c.executemany("""
        INSERT OR REPLACE INTO ships (name, price, base_speed, capacity, sails_multiplier, png)
        VALUES (?, ?, ?, ?, ?, ?)
    """, ships)

    # Insert enemy ships
    c.executemany("""
        INSERT OR REPLACE INTO enemy_vessels_data (name, price, base_speed, capacity, sails_multiplier, png)
        VALUES (?, ?, ?, ?, ?, ?)
    """, enemy_vessels_data)

    conn.commit()
    conn.close()
    print(f"✅ {len(ships)} player ships and {len(enemy_vessels_data)} enemy ships populated!")


def populate_enemy_ships():
    """Populate enemy ships into the database"""
    conn = sqlite3.connect(SHIP_DB_PATH)
    c = conn.cursor()

    # Create enemy ships table if it doesn't exist
    c.execute("""
        CREATE TABLE IF NOT EXISTS enemy_vessels_data (
            name TEXT PRIMARY KEY,
            price REAL,
            base_speed REAL,
            capacity INTEGER,
            sails_multiplier REAL,
            png TEXT
        )
    """)

    # Clear existing data
    c.execute("DELETE FROM enemy_vessels_data")

    # Insert enemy ships
    c.executemany("""
        INSERT OR REPLACE INTO enemy_vessels_data 
        (name, price, base_speed, capacity, sails_multiplier, png)
        VALUES (?, ?, ?, ?, ?, ?)
    """, enemy_vessels_data)

    conn.commit()
    conn.close()
    print(f"✅ {len(enemy_vessels_data)} enemy ships populated into database!")

def get_item_db_connection():
    """Get connection to item database"""
    return sqlite3.connect(ITEM_DB_PATH)

def get_ship_db_connection():
    """Get connection to ship database"""
    print(f"DEBUG: Connecting to SHIP_DB_PATH → {SHIP_DB_PATH}")
    return sqlite3.connect(SHIP_DB_PATH)

# Example usage functions:
def get_all_items():
    """Get all items from the item market"""
    conn = get_item_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM items")
    items = c.fetchall()
    conn.close()
    return items

def get_all_ships():
    """Get all ships from the ship market"""
    conn = get_ship_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM ships")
    ships = c.fetchall()
    conn.close()
    return ships

def get_all_enemy_ships():
    """Get all enemy ships"""
    conn = get_ship_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM enemy_ships")
    enemy_ships = c.fetchall()
    conn.close()
    return enemy_ships


if __name__ == "__main__":
    # Initialize both databases
    init_databases()

    # Populate both databases
    # Populate all data
    populate_items()
    populate_ships()
    populate_enemy_ships()

    print("✅ Both databases initialized and populated!")
    print(f"Item database: {ITEM_DB_PATH}")
    print(f"Ship database: {SHIP_DB_PATH}")