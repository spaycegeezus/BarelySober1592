import os

def quick_missing_analysis():
    """Quick analysis of missing database entries."""
    ASSETS_DIR = "Assets"

    # Get PNG files
    asset_pngs = {f.lower() for f in os.listdir(ASSETS_DIR) if f.lower().endswith('.png')}

    # Your current combat items from the code above
    current_combat_pngs = {
        "dull_dagger.png", "dull_sword.png", "cracked_canon.png", "dagger.png", "sword.png",
        "canon.png", "rusty_cutlass.png", "polished_cutlass.png", "ornate_cutlass.png",
        "iron_dagger.png", "silver_dagger.png", "jeweled_dagger.png", "rusty_saber.png",
        "fancy_saber.png", "captains_saber.png", "wooden_club.png", "iron_club.png",
        "spiked_club.png", "short_spear.png", "steel_spear.png", "ornate_spear.png",
        "battle_axe.png", "ornate_axe.png", "executioner_axe.png", "rusty_rapier.png",
        "silver_rapier.png", "royal_rapier.png", "cracked_pistol.png", "flintlock_pistol.png",
        "dual_ornate_pistols.png", "throwing_knife.png", "balanced_knife.png",
        "assassins_knife.png", "crude_halbred.png", "steel_halbred.png", "royal_halbred.png"
    }

    # Find PNGs that aren't in your combat items
    non_combat_pngs = asset_pngs - current_combat_pngs

    print(f"Total PNG files: {len(asset_pngs)}")
    print(f"Combat item PNGs: {len(current_combat_pngs)}")
    print(f"Non-combat PNGs available: {len(non_combat_pngs)}")

    print("\n=== NON-COMBAT PNG FILES AVAILABLE ===")
    for png in sorted(non_combat_pngs):
        print(f"'{png}'")


# Run the quick analysis
quick_missing_analysis()