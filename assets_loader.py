# assets_loader.py
import os
from kivy.core.image import Image as CoreImage

ASSETS_DIR = "Assets"

ASSET_FILES = {
    "random / animations": {
        "demon_dice" : "demon_dice.png",
        "dice_five": "dice_five.png",
        "dice_four": "dice_four.png",
        "dice_three": "dice_three.png",
        "dice_two": "dice_two.png",
        "dice_one": "dice_one.png",
        "dice_six": "dice_six.png",
        "medium_dice": "medium_dice.png",
        "wooden_dice": "wooden_dice.png",
        "pile_dice": "pile_dice.png",
        "shadow": "shadow.png",
        "swim_twist": "swim_twist.png",
        "swim_twist_down": "swim_twist_down.png",
        "swim_twist_up": "swim_twist_up.png",
        "swim_upstroke": "swim_upstroke.png",
        "swim_down_stroke": "swim_down_stroke.png",
        "pearl": "pearl.png",

    },

    "maps": {
        "ancient": "ancient_map.png",
        "monster": "monster_map.png",
        "navigators_map": "navigators_map.png",
    },
    "background":{
        "calm_ocean": "calm_ocean.png",
        "canon_deck": "canon_deck.png",
        "captain_quarters": "captain_quarters.png",
        "harbor": "harbor.png",
        "gambling_table": "gambling_table.png",
        "item_market": "item_market.png",
        "monkey_treasure": "monkey_treasure.png",
        "rough_ocean": "rough_ocean.png",
        "ship_market": "ship_market.png",
        "wave": "wave.png",

    },
    "title": {
        "barely": "barelysobertitle.png",
        "gambling_table": "gambling_table.png",
        "navigating_the_unknown_title.png": "navigating_the_unknown_title.png",
        "navigating_the_unknown_title_white.png": "navigating_the_unknown_title_white.png",
        "captainquartertitle": "captain_quarter_title.png",
        "vessel": "vessel_and_cargo_title.png",
    },
    "combat": {
        # axes, clubs, and spears
        "battle_axe": "battle_axe.png",
        "crude_halberd": "crude_halberd.png",
        "executioner_axe": "executioner_axe.png",
        "wooden_club": "wooden_club.png",
        "iron_club": "iron_club.png",
        "ornate_axe": "ornate_axe.png",
        "ornate_spear": "ornate_spear.png",
        "royal_halberd": "royal_halberd.png",
        "short_spear": "short_spear.png",
        "spiked_club": "spiked_club.png",
        "steel_halberd": "steel_halberd.png",
        "steel_spear": "steel_spear.png",

        #guns and rifles
        "throwing_knife": "throwing_knife.png",
        "blunderbuss": "blunderbuss.png",
        "cracked_pistol": "cracked_pistol.png",
        "dual_ornate_pistols": "dual_ornate_pistols.png",
        "flintlock_pistol": "flintlock_pistol.png",
        "flintlock_rifle": "flintlock_rifle.png",
        "long_rifle": "long_rifle.png",
        "ornate_rifle": "ornate_rifle.png",

        # Swords, Sabers, and Cutlasses
        "dagger": "dagger.png",
        "dull_dagger": "dull_dagger.png",
        "rusty_dagger": "rusty_dagger.png",
        "iron_dagger": "iron_dagger.png",
        "silver_dagger": "silver_dagger.png",
        "jeweled_dagger": "jeweled_dagger.png",
        "polished_cutlass": "polished_cutlass.png",
        "silver_cutlass": "silver_cutlass.png",
        "fancy_cutlass": "fancy_cutlass.png",
        "rusty_cutlass": "rusty_cutlass.png",
        "ornate_cutlass": "ornate_cutlass.png",
        "ornate_saber": "ornate_saber.png",
        "captain_saber": "captain_saber.png",
        "fancy_saber": "fancy_saber.png",
        "rusty_saber": "rusty_saber.png",
        "rusty_sword": "rusty_sword.png",
        "dull_sword": "dull_sword.png",
        "sword": "sword.png",
        "captain_sword": "captain_sword.png",
        "magic_sword": "magic_sword.png",
        "rusty_rapier": "rusty_rapier.png",
        "silver_rapier": "silver_rapier.png",
        "royal_rapier": "royal_rapier.png",

        # canons and Artillery
        "canon": "canon.png",
        "canon_royal": "canon_royal.png",
        "12_pound_canon": "12_pound_canon.png",
        "culverin_canon": "culverin_canon.png",
        "demi_canon": "demi_canon.png",
        "deck_canon": "deck_canon.png",
        "falcon_canon": "falcon_canon.png",
        "murderer_canon": "murderer_canon.png",
        "robinet_canon": "robinet_canon.png",
        "saker_canon": "saker_canon.png",
        "canon_shot_bar": "canon_shot_bar.png",
        "canon_shot_chain": "canon_shot_chain.png",
        "canon_shot_fuse": "canon_shot_fuse.png",
        "canon_shot_round": "canon_shot_round.png",
        "canon_shot_grape": "canon_shot_grape.png",

    },

    "storage/sails": {
        "cargo_net": "cargo_net.png",
        "cotton_sail": "cotton_sail.png",
        "crate": "crate.png",
        "endless_barrel": "endless_barrel.png",
        "large_barrels": "large_barrels.png",
        "linen_sail": "linen_sail.png",
        "magic_chest": "magic_chest.png",
        "magic_crate": "magic_crate.png",
        "magic_rope": "magic_rope.png",
        "medium_barrel": "medium_barrel.png",
        "mystic_satchel": "mystic_satchel.png",
        "mythical_chest": "mythical_chest.png",
        "rope": "rope.png",
        "rope_coil": "rope_coil.png",
        "silk_sail": "silk_sail.png",
        "small_barrel": "small_barrel.png",
        "sturdy_crate": "sturdy_crate.png",
        "sturdy_rope": "sturdy_rope.png",

    },

    "treasure": {
        "chest": "treasure_chest.png",
        "bag_gold": "bag_gold.png",
        "gold_coins": "gold_coins.png",
        "capatin_chest": "captain_chest.png",
        "treasure_chest": "treasure_chest.png",

    },
    "navigation": {
        "compass": "compass.png",
        "cheap_compass": "cheap_compass.png",
        "brass_compass": "brass_compass.png",
        "fancy_compass": "fancy_compass.png",
        "magic_compass": "magic_compass.png",
        "sextant": "sextant.png",
    },
    "drinks": {
        "grog": "grog.png",
        "wine": "glass_wine.png",
        "tea": "cup_tea.png",
        "aztec_tequila": "aztec_tequila.png",
        "absinthe": "absinthe.png",
        "bottle": "bottle.png",
        "clasped_bottle": "clasped_bottle.png",
        "caribbean_firewater": "caribbean_firewater.png",
        "cognac": "cognac.png",
        "gin": "gin.png",
        "glass_wine": "glass_wine.png",
        "grapa_wine": "grapa_wine.png",
        "jaeger": "jaeger.png",
        "hooked_goblet": "hooked_goblet.png",
        "long_bottle": "long_bottle.png",
        "magic_bottle": "magic_bottle.png",
        "mead": "mead.png",
        "mermaids_nectar": "mermaids_nectar.png",
        "mystic_bottle": "mystic_bottle.png",
        "phoenix_firewater": "phoenix_firewater.png",
        "pirate_rum": "pirate_rum.png",
        "poseidon_elixir": "poseidon_elixir.png",
        "rum_bottle": "rum_bottle.png",
        "samurai_sake": "samurai_sake.png",
        "shaman_vodka": "shaman_vodka.png",
        "silver_tequila": "silver_tequila.png",
        "tequila": "tequila.png",
        "vodka": "vodka.png",
        "whiskey_cask": "whiskey_cask.png",
        "whiskey_shot": "whiskey_shot.png",
        "wine_barrel": "wine_barrel.png",
        "wine_bottle": "wine_bottle.png",


    "food": {
        "apple": "apple.png",
        "bananas": "bananas.png",
        "boar_roast": "boar_roast.png",
        "brie": "brie.png",
        "bushel_apples": "bushel_apples.png",
        "buttered_cod": "buttered_cod.png",
        "cheese_platter": "cheese_platter.png",
        "cheese_wedge": "cheese_wedge.png",
        "crate_oranges": "crate_oranges.png",
        "cured_ham": "cured_ham.png",
        "dried_figs": "dried_figs.png",
        "dried_fish": "dried_fish.png",
        "grilled_fish": "grilled_fish.png",
        "fresh_bread": "fresh_bread.png",
        "fresh_water": "fresh_water.png",
        "goose_feast": "goose_feast.png",
        "grapes": "grapes.png",
        "gruel": "gruel.png",
        "hardtack": "hard_tack.png",
        "honeycomb": "honeycomb.png",
        "lentils": "lentils.png",
        "lobster_stew": "lobster_stew.png",
        "meat_pie": "meat_pie.png",
        "pomegranate": "pomegranate.png",
        "roasted_chicken": "roasted_chicken.png",
        "salted_pork": "salted_pork.png",
        "smoked_eel": "smoked_eel.png",
        "spiced_stew": "spiced_stew.png",
        "stale_bread": "stale_bread.png",
        "steak_pie": "steak_pie.png",
        "steamed_barley": "steamed_barley.png",
        "stew": "stew.png",
        "swan_feast": "swan_feast.png",
        "venison_pie": "venison_pie.png",
    }
    },

    "sea_creatures": {
        "shark_body": "shark_body.png",
        "shark_face": "shark_face.png",
        "shark_teeth": "shark_teeth.png",
        "shark_bite": "shark_bite.png",
        "shark_growl": "shark_growl.png",
        "shark_swim": "shark_swim.png",
        "shark_turn": "shark_turn.png",
        "fish": "fish.png",
        "fish_bigfins": "fish_bigfins.png",
        "humpback": "humpback.png",
        "whale": "whale.png",
        "shark": "shark.png",
        "jellyfish": "jellyfish.png",
    },
    "lighting": {
        "candle": "candle.png",
        "brass_lantern": "brass_lantern.png",
        "iron_lantern": "iron_lantern.png",
        "magic_lantern": "magic_lantern.png",
    },
    "vessels": {
        # ------------------------
        # Small Ships / Starter Tier
        # ------------------------
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
        "galleon": "galleon.png",
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

        # extra ship images
        "boat": "boat.png",
        "side_half_sail": "ship_side_halfsail.png",
        "side_full_stop": "side_ship_fullstop.png",
        "side_threequarter_sail": "side_ship_threequarter_sail.png",
        "rear_stop": "rear_ship_stop.png",
        "rear_view_canon": "rear_view_canon.png",
        "enemy_galleon": "enemy_galleon.png",
        "enemy_brig": "enemy_brig.png",
        "enemy_sloop": "enemy_sloop.png",
        "enemy_ghost_ship": "enemy_ghost_ship.png",
        "enemy_naval_frigate": "enemy_naval_frigate.png",
        "enemy_caravel": "enemy_caravel.png",
        "enemy_carrack": "enemy_carrack.png",
        "cursed_schooner_ship": "cursed_schooner_ship.png",
        "enemy_frigate":  "enemy_frigate.png",
        "enemy_black_sail": "enemy_black_sail.png",
        "tall_ship": "tall_ship.png",
        "cursed_sloop_ship": "cursed_sloop_ship.png",
        "corsair_raider_ship": "corsair_raider_ship.png",
        "galleon_print": "galleon_print.png",
        "phoenix_galleon_ship": "phoenix_galleon_ship.png",
        "ship_print": "ship_print.png",
        "sinking_ship": "sinking_ship.png",
        "smuggler_sloop": "smuggler_sloop.png",
        "war_ship": "war_ship.png",
        "manowar_print": "manowar_print.png",
        "cutter_print": "cutter_print.png",
        "leviathan_print": "leviathan_print.png",
        "serpant_ship": "serpent_ship.png",

    }
}

# Global cache
ASSETS = {}

def preload_assets():
    """Recursively preload all textures into ASSETS global dict."""
    def load_recursive(base_dict, sub_dir=""):
        loaded = {}
        for key, val in base_dict.items():
            if isinstance(val, dict):
                # Recursively load subcategories
                loaded[key] = load_recursive(val, sub_dir)
            else:
                # Construct file path
                path = os.path.join(ASSETS_DIR, sub_dir, val)
                if not os.path.exists(path):
                    print(f"[WARNING] Missing asset: {path}")
                    continue
                try:
                    loaded[key] = CoreImage(path).texture
                except Exception as e:
                    print(f"[ERROR] Failed to load {path}: {e}")
        return loaded

    global ASSETS
    ASSETS = load_recursive(ASSET_FILES)
    return ASSETS

def handle_missing_image(image_path):
    """Handle missing images by providing a placeholder."""
    placeholder_path = "Assets/placeholder.png"
    # Create a simple placeholder if it doesn't exist
    if not os.path.exists(placeholder_path):
        # You could create a simple colored rectangle as placeholder
        from PIL import Image, ImageDraw
        img = Image.new('RGB', (64, 64), color='red')
        draw = ImageDraw.Draw(img)
        draw.text((10, 25), "?", fill='white')
        img.save(placeholder_path)
    return placeholder_path