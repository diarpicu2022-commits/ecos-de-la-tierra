"""Utilidades compartidas para generar el pixel art de *Ecos de la Tierra*.

La paleta es la del contrato «Ceniza y Brasa» (bloqueado el 2026-09-13). Ningún
sprite introduce un color que no salga de aquí: así el mundo entero comparte la
misma rampa de ceniza y el verde conserva un único significado.

El ruido es determinista: con la misma semilla sale exactamente el mismo sprite,
de modo que regenerar los assets no cambia el juego por sorpresa.
"""

from __future__ import annotations

import math
import random

from PIL import Image

# --- Paleta del contrato -----------------------------------------------------

PALETTE: dict[str, tuple[int, int, int, int]] = {
    # Ceniza: estructura del mundo apagado.
    "ash_950": (0x17, 0x14, 0x1C, 255),
    "ash_900": (0x22, 0x1D, 0x2A, 255),
    "ash_800": (0x2E, 0x28, 0x36, 255),
    "ash_700": (0x3A, 0x35, 0x40, 255),
    "ash_600": (0x4D, 0x46, 0x57, 255),
    "ash_400": (0x9C, 0x95, 0xA7, 255),
    "ash_200": (0xB8, 0xB0, 0xC4, 255),
    "ash_050": (0xE8, 0xE4, 0xEE, 255),
    # Brasa: el daño y la causa todavía activa.
    "ember_700": (0x7A, 0x25, 0x18, 255),  # Borde apagado de la llama.
    "ember_500": (0xE8, 0x56, 0x2E, 255),
    "ember_400": (0xF0, 0x8A, 0x3C, 255),
    "ember_300": (0xFF, 0xC1, 0x4D, 255),
    # Acento único: la purificación.
    "vital_500": (0x4A, 0xDE, 0x80, 255),
    "vital_700": (0x2B, 0x9D, 0x5A, 255),
    "vital_900": (0x1A, 0x5E, 0x38, 255),
    # Mundo: tres rampas de material, enmienda 1 del contrato «Vereda»
    # (2026-09-14). Techo de saturación 0,22: el mundo sigue apagado.
    "soil_700": (0x40, 0x37, 0x32, 255),
    "soil_500": (0x59, 0x4D, 0x46, 255),
    "soil_300": (0x73, 0x64, 0x5A, 255),
    "water_700": (0x1E, 0x24, 0x26, 255),
    "water_500": (0x36, 0x41, 0x45, 255),
    "water_300": (0x4E, 0x5E, 0x63, 255),
    "flora_700": (0x43, 0x45, 0x36, 255),
    "flora_500": (0x57, 0x59, 0x46, 255),
    "flora_300": (0x6A, 0x6E, 0x56, 255),
    # Enmienda 6 (2026-10-28): rampas de lo construido, cinco tonos, bajo el
    # techo de 0,22. La piedra sale de la ceniza: no lleva rampa propia.
    "wood_900": (0x2B, 0x26, 0x22, 255),
    "wood_700": (0x45, 0x3D, 0x36, 255),
    "wood_500": (0x61, 0x56, 0x4D, 255),
    "wood_300": (0x82, 0x73, 0x67, 255),
    "wood_100": (0xA6, 0x93, 0x83, 255),
    "roof_900": (0x33, 0x2A, 0x28, 255),
    "roof_700": (0x4C, 0x40, 0x3C, 255),
    "roof_500": (0x6B, 0x59, 0x55, 255),
    "roof_300": (0x8C, 0x75, 0x6F, 255),
    "roof_100": (0xAD, 0x90, 0x89, 255),
    # Enmienda 6: color de lo purificado, por encima del techo. Solo en
    # celdas purificadas: el agua viva, las flores y el verde claro de la hoja.
    "aqua_900": (0x12, 0x48, 0x5C, 255),
    "aqua_700": (0x2B, 0x74, 0x8F, 255),
    "aqua_500": (0x51, 0xA8, 0xC2, 255),
    "aqua_300": (0x85, 0xD5, 0xE6, 255),
    "aqua_100": (0xD2, 0xF7, 0xFA, 255),
    "bloom_900": (0x7A, 0x31, 0x5C, 255),
    "bloom_700": (0xBD, 0x5B, 0x88, 255),
    "bloom_500": (0xF2, 0x85, 0xA6, 255),
    "bloom_300": (0xC6, 0x8E, 0xE6, 255),
    "bloom_100": (0xAA, 0xCF, 0xFA, 255),
    "vital_300": (0x91, 0xF2, 0xB2, 255),
    # Hierba del prado purificado: más amarilla que el acento, para que un
    # prado entero no sea un campo de VITAL_500.
    "vital_600": (0x54, 0xB2, 0x50, 255),
    "vital_400": (0x86, 0xD6, 0x6B, 255),
    # --- TIERRA VIVA: BEGIN (enmienda 13). Generado por gen_tierra_viva_tokens.py ---
    "tv_ink_0": (0x14, 0x10, 0x1C, 255),
    "tv_ink_1": (0x23, 0x1C, 0x2E, 255),
    "tv_ink_2": (0x37, 0x2B, 0x42, 255),
    "tv_stone_0": (0x2A, 0x24, 0x34, 255),
    "tv_stone_1": (0x40, 0x38, 0x4D, 255),
    "tv_stone_2": (0x5C, 0x52, 0x68, 255),
    "tv_stone_3": (0x7D, 0x73, 0x87, 255),
    "tv_stone_4": (0xA1, 0x98, 0xA8, 255),
    "tv_stone_5": (0xC9, 0xC1, 0xCC, 255),
    "tv_stone_6": (0xEC, 0xE6, 0xEC, 255),
    "tv_grass_0": (0x12, 0x3A, 0x2E, 255),
    "tv_grass_1": (0x1A, 0x52, 0x34, 255),
    "tv_grass_2": (0x25, 0x6E, 0x3A, 255),
    "tv_grass_3": (0x35, 0x8C, 0x3E, 255),
    "tv_grass_4": (0x4F, 0xA6, 0x45, 255),
    "tv_grass_5": (0x7C, 0xC4, 0x56, 255),
    "tv_grass_6": (0xB5, 0xE0, 0x73, 255),
    "tv_leaf_0": (0x0F, 0x2B, 0x26, 255),
    "tv_leaf_1": (0x17, 0x42, 0x32, 255),
    "tv_leaf_2": (0x21, 0x5C, 0x38, 255),
    "tv_leaf_3": (0x2F, 0x7A, 0x3C, 255),
    "tv_leaf_4": (0x48, 0x98, 0x3F, 255),
    "tv_leaf_5": (0x74, 0xB8, 0x4A, 255),
    "tv_leaf_6": (0xAA, 0xD6, 0x5E, 255),
    "tv_dirt_0": (0x3B, 0x22, 0x26, 255),
    "tv_dirt_1": (0x5A, 0x33, 0x2C, 255),
    "tv_dirt_2": (0x7D, 0x4B, 0x35, 255),
    "tv_dirt_3": (0xA0, 0x67, 0x41, 255),
    "tv_dirt_4": (0xC4, 0x8A, 0x52, 255),
    "tv_dirt_5": (0xE0, 0xB0, 0x70, 255),
    "tv_dirt_6": (0xF4, 0xD6, 0x99, 255),
    "tv_sand_0": (0x8A, 0x6A, 0x4A, 255),
    "tv_sand_1": (0xB0, 0x8D, 0x5E, 255),
    "tv_sand_2": (0xD1, 0xB0, 0x77, 255),
    "tv_sand_3": (0xE8, 0xCF, 0x98, 255),
    "tv_sand_4": (0xF7, 0xEB, 0xC4, 255),
    "tv_water_0": (0x16, 0x24, 0x4F, 255),
    "tv_water_1": (0x1B, 0x3C, 0x7A, 255),
    "tv_water_2": (0x23, 0x60, 0xA8, 255),
    "tv_water_3": (0x34, 0x89, 0xCC, 255),
    "tv_water_4": (0x56, 0xB3, 0xE6, 255),
    "tv_water_5": (0x92, 0xD9, 0xF4, 255),
    "tv_water_6": (0xDF, 0xF7, 0xFF, 255),
    "tv_wood_0": (0x2E, 0x1A, 0x1E, 255),
    "tv_wood_1": (0x4A, 0x2A, 0x26, 255),
    "tv_wood_2": (0x6B, 0x3F, 0x2E, 255),
    "tv_wood_3": (0x8F, 0x5A, 0x3A, 255),
    "tv_wood_4": (0xB2, 0x7A, 0x4C, 255),
    "tv_wood_5": (0xD1, 0xA0, 0x68, 255),
    "tv_roof_red_0": (0x3A, 0x14, 0x26, 255),
    "tv_roof_red_1": (0x5E, 0x1F, 0x30, 255),
    "tv_roof_red_2": (0x8C, 0x2C, 0x3A, 255),
    "tv_roof_red_3": (0xB8, 0x44, 0x3F, 255),
    "tv_roof_red_4": (0xDC, 0x6A, 0x4C, 255),
    "tv_roof_red_5": (0xF2, 0x9C, 0x6E, 255),
    "tv_roof_blue_0": (0x1A, 0x1D, 0x40, 255),
    "tv_roof_blue_1": (0x25, 0x33, 0x66, 255),
    "tv_roof_blue_2": (0x2F, 0x4F, 0x94, 255),
    "tv_roof_blue_3": (0x3F, 0x75, 0xBE, 255),
    "tv_roof_blue_4": (0x62, 0xA2, 0xDC, 255),
    "tv_roof_blue_5": (0x9C, 0xCD, 0xF0, 255),
    "tv_wall_0": (0x6B, 0x5A, 0x66, 255),
    "tv_wall_1": (0x8F, 0x7D, 0x82, 255),
    "tv_wall_2": (0xB5, 0xA5, 0x98, 255),
    "tv_wall_3": (0xD8, 0xCB, 0xB4, 255),
    "tv_wall_4": (0xF2, 0xE8, 0xD2, 255),
    "tv_flower_0": (0xB0, 0x30, 0x4F, 255),
    "tv_flower_1": (0xE8, 0x56, 0x6B, 255),
    "tv_flower_2": (0xFF, 0x8F, 0xA3, 255),
    "tv_flower_3": (0xFF, 0xD3, 0x4E, 255),
    "tv_flower_4": (0xFF, 0xF3, 0xB0, 255),
    "tv_flower_5": (0x8A, 0x6B, 0xD9, 255),
    "tv_flower_6": (0xC3, 0xA8, 0xFF, 255),
    "tv_flower_7": (0xFF, 0xFF, 0xFF, 255),
    "tv_dry_grass_0": (0x2A, 0x1F, 0x2A, 255),
    "tv_dry_grass_1": (0x3D, 0x2E, 0x2E, 255),
    "tv_dry_grass_2": (0x56, 0x43, 0x2F, 255),
    "tv_dry_grass_3": (0x73, 0x5C, 0x37, 255),
    "tv_dry_grass_4": (0x94, 0x78, 0x3F, 255),
    "tv_dry_grass_5": (0xB3, 0x9A, 0x52, 255),
    "tv_dry_grass_6": (0xCF, 0xBD, 0x70, 255),
    "tv_dead_leaf_0": (0x1E, 0x16, 0x22, 255),
    "tv_dead_leaf_1": (0x2F, 0x22, 0x29, 255),
    "tv_dead_leaf_2": (0x46, 0x33, 0x2E, 255),
    "tv_dead_leaf_3": (0x61, 0x48, 0x3A, 255),
    "tv_dead_leaf_4": (0x7F, 0x61, 0x46, 255),
    "tv_dead_leaf_5": (0x9C, 0x7D, 0x55, 255),
    "tv_ash_0": (0x22, 0x1D, 0x29, 255),
    "tv_ash_1": (0x34, 0x2D, 0x3B, 255),
    "tv_ash_2": (0x4A, 0x42, 0x52, 255),
    "tv_ash_3": (0x64, 0x5C, 0x6B, 255),
    "tv_ash_4": (0x82, 0x7A, 0x88, 255),
    "tv_ash_5": (0xA3, 0x9C, 0xA6, 255),
    "tv_ash_6": (0xC7, 0xC1, 0xC6, 255),
    "tv_oil_0": (0x0B, 0x08, 0x12, 255),
    "tv_oil_1": (0x15, 0x11, 0x1F, 255),
    "tv_oil_2": (0x22, 0x1B, 0x30, 255),
    "tv_oil_3": (0x30, 0x27, 0x44, 255),
    "tv_oil_4": (0x43, 0x37, 0x57, 255),
    "tv_sheen_0": (0x5A, 0x3F, 0x8C, 255),
    "tv_sheen_1": (0x3F, 0x7F, 0x86, 255),
    "tv_sheen_2": (0xA3, 0x96, 0x3F, 255),
    "tv_sheen_3": (0xC0, 0x57, 0x7A, 255),
    "tv_sludge_0": (0x2F, 0x3A, 0x12, 255),
    "tv_sludge_1": (0x4F, 0x64, 0x18, 255),
    "tv_sludge_2": (0x77, 0x92, 0x1F, 255),
    "tv_sludge_3": (0xA4, 0xC4, 0x2C, 255),
    "tv_sludge_4": (0xD2, 0xEF, 0x5A, 255),
    "tv_smog_0": (0x4B, 0x3F, 0x4A, 255),
    "tv_smog_1": (0x6E, 0x5D, 0x62, 255),
    "tv_smog_2": (0x93, 0x80, 0x7A, 255),
    "tv_smog_3": (0xB8, 0xA5, 0x94, 255),
    "tv_rust_0": (0x3A, 0x1A, 0x16, 255),
    "tv_rust_1": (0x5E, 0x2A, 0x1E, 255),
    "tv_rust_2": (0x8A, 0x41, 0x26, 255),
    "tv_rust_3": (0xB5, 0x60, 0x2F, 255),
    "tv_rust_4": (0xD6, 0x8A, 0x45, 255),
    "tv_plastic_0": (0x2A, 0x4F, 0x6E, 255),
    "tv_plastic_1": (0x3F, 0x7F, 0xA8, 255),
    "tv_plastic_2": (0x7C, 0xC0, 0xE0, 255),
    "tv_plastic_3": (0xC9, 0xEC, 0xF7, 255),
    "tv_plastic_4": (0xE2, 0x5A, 0x6A, 255),
    "tv_plastic_5": (0xF2, 0xC9, 0x4C, 255),
    "tv_plastic_6": (0xFF, 0xFF, 0xFF, 255),
    "tv_fire_0": (0x3D, 0x0F, 0x14, 255),
    "tv_fire_1": (0x7A, 0x1A, 0x16, 255),
    "tv_fire_2": (0xC1, 0x3A, 0x1C, 255),
    "tv_fire_3": (0xEC, 0x6A, 0x24, 255),
    "tv_fire_4": (0xFF, 0xA8, 0x3A, 255),
    "tv_fire_5": (0xFF, 0xE0, 0x7A, 255),
    "tv_fire_6": (0xFF, 0xFB, 0xE0, 255),
    "tv_ice_0": (0x1D, 0x2C, 0x52, 255),
    "tv_ice_1": (0x2C, 0x4C, 0x80, 255),
    "tv_ice_2": (0x4A, 0x7F, 0xB4, 255),
    "tv_ice_3": (0x7A, 0xB6, 0xDF, 255),
    "tv_ice_4": (0xB0, 0xE0, 0xF4, 255),
    "tv_ice_5": (0xE4, 0xF8, 0xFF, 255),
    "tv_gold_0": (0x3A, 0x24, 0x12, 255),
    "tv_gold_1": (0x6B, 0x43, 0x16, 255),
    "tv_gold_2": (0xA6, 0x70, 0x1C, 255),
    "tv_gold_3": (0xD9, 0xA5, 0x2A, 255),
    "tv_gold_4": (0xF5, 0xD2, 0x4A, 255),
    "tv_gold_5": (0xFF, 0xF1, 0xA0, 255),
    "tv_eco_0": (0x0F, 0x3B, 0x3F, 255),
    "tv_eco_1": (0x14, 0x70, 0x6A, 255),
    "tv_eco_2": (0x20, 0xA8, 0x8F, 255),
    "tv_eco_3": (0x4F, 0xD8, 0xB0, 255),
    "tv_eco_4": (0x9C, 0xF5, 0xD4, 255),
    "tv_eco_5": (0xE2, 0xFF, 0xF3, 255),
    "tv_turbid_0": (0x1F, 0x2A, 0x2C, 255),
    "tv_turbid_1": (0x2C, 0x3A, 0x3A, 255),
    "tv_turbid_2": (0x3B, 0x4A, 0x48, 255),
    "tv_turbid_3": (0x4B, 0x5A, 0x55, 255),
    "tv_turbid_4": (0x5F, 0x6D, 0x66, 255),
    "tv_turbid_5": (0x7D, 0x87, 0x7C, 255),
    "tv_turbid_6": (0xA3, 0xA8, 0x98, 255),
    "tv_oil_water_0": (0x07, 0x05, 0x0C, 255),
    "tv_oil_water_1": (0x11, 0x0C, 0x1A, 255),
    "tv_oil_water_2": (0x1B, 0x14, 0x28, 255),
    "tv_oil_water_3": (0x26, 0x1D, 0x36, 255),
    "tv_oil_water_4": (0x3A, 0x2C, 0x4C, 255),
    "tv_oil_water_5": (0x5A, 0x3F, 0x8C, 255),
    "tv_oil_water_6": (0x3F, 0x7F, 0x86, 255),
    "tv_plastic_water_0": (0x1D, 0x2A, 0x33, 255),
    "tv_plastic_water_1": (0x2A, 0x3B, 0x45, 255),
    "tv_plastic_water_2": (0x3A, 0x4D, 0x57, 255),
    "tv_plastic_water_3": (0x4B, 0x5F, 0x68, 255),
    "tv_plastic_water_4": (0x61, 0x75, 0x7B, 255),
    "tv_plastic_water_5": (0x83, 0x93, 0x93, 255),
    "tv_plastic_water_6": (0xB5, 0xBF, 0xBB, 255),
    "tv_sludge_grass_0": (0x1F, 0x1D, 0x14, 255),
    "tv_sludge_grass_1": (0x2B, 0x2A, 0x19, 255),
    "tv_sludge_grass_2": (0x3A, 0x38, 0x20, 255),
    "tv_sludge_grass_3": (0x4B, 0x48, 0x26, 255),
    "tv_sludge_grass_4": (0x5D, 0x59, 0x2D, 255),
    "tv_sludge_grass_5": (0x77, 0x71, 0x3A, 255),
    "tv_sludge_grass_6": (0x93, 0x8B, 0x4C, 255),
    "tv_grey_sand_0": (0x7D, 0x74, 0x66, 255),
    "tv_grey_sand_1": (0x98, 0x8E, 0x7D, 255),
    "tv_grey_sand_2": (0xB0, 0xA6, 0x90, 255),
    "tv_grey_sand_3": (0xC4, 0xBA, 0xA2, 255),
    "tv_grey_sand_4": (0xD6, 0xCD, 0xB6, 255),
    "tv_paramo_0": (0x1C, 0x2F, 0x2A, 255),
    "tv_paramo_1": (0x2A, 0x44, 0x34, 255),
    "tv_paramo_2": (0x3D, 0x5C, 0x3A, 255),
    "tv_paramo_3": (0x58, 0x7A, 0x42, 255),
    "tv_paramo_4": (0x7A, 0x95, 0x4C, 255),
    "tv_paramo_5": (0xA3, 0xB4, 0x5E, 255),
    "tv_paramo_6": (0xCD, 0xD1, 0x7C, 255),
    "tv_snow_0": (0x7D, 0x8F, 0xB8, 255),
    "tv_snow_1": (0xA9, 0xBB, 0xD9, 255),
    "tv_snow_2": (0xCF, 0xDC, 0xEF, 255),
    "tv_snow_3": (0xE9, 0xF1, 0xFA, 255),
    "tv_snow_4": (0xFF, 0xFF, 0xFF, 255),
    "tv_paramo_dry_0": (0x2A, 0x22, 0x26, 255),
    "tv_paramo_dry_1": (0x3D, 0x30, 0x2C, 255),
    "tv_paramo_dry_2": (0x56, 0x43, 0x2F, 255),
    "tv_paramo_dry_3": (0x6E, 0x58, 0x38, 255),
    "tv_paramo_dry_4": (0x8A, 0x70, 0x44, 255),
    "tv_paramo_dry_5": (0xA5, 0x8A, 0x55, 255),
    "tv_paramo_dry_6": (0xBE, 0xA5, 0x6A, 255),
    "tv_scree_0": (0x3E, 0x39, 0x43, 255),
    "tv_scree_1": (0x57, 0x50, 0x5A, 255),
    "tv_scree_2": (0x72, 0x6A, 0x72, 255),
    "tv_scree_3": (0x8F, 0x87, 0x8C, 255),
    "tv_scree_4": (0xAC, 0xA4, 0xA6, 255),
    "tv_sick_soil_0": (0x2A, 0x22, 0x26, 255),
    "tv_sick_soil_1": (0x3D, 0x32, 0x2F, 255),
    "tv_sick_soil_2": (0x54, 0x46, 0x3D, 255),
    "tv_sick_soil_3": (0x6F, 0x5F, 0x50, 255),
    "tv_sick_soil_4": (0x8C, 0x7A, 0x64, 255),
    "tv_sick_soil_5": (0xA8, 0x95, 0x7A, 255),
    "tv_sick_soil_6": (0xC2, 0xB0, 0x92, 255),
    "tv_frailejon_0": (0x4D, 0x6A, 0x4A, 255),
    "tv_frailejon_1": (0x7B, 0x96, 0x70, 255),
    "tv_frailejon_2": (0xA7, 0xBC, 0x9A, 255),
    "tv_frailejon_3": (0xCF, 0xDC, 0xC4, 255),
    "tv_frailejon_4": (0xEE, 0xF4, 0xE6, 255),
    "tv_puya_0": (0x2D, 0x4A, 0x3C, 255),
    "tv_puya_1": (0x46, 0x6B, 0x4C, 255),
    "tv_puya_2": (0x6A, 0x8F, 0x62, 255),
    "tv_puya_3": (0x94, 0xB1, 0x83, 255),
    "tv_puya_4": (0xC3, 0xD6, 0xAE, 255),
    "tv_straw_0": (0x56, 0x50, 0x2E, 255),
    "tv_straw_1": (0x7D, 0x72, 0x38, 255),
    "tv_straw_2": (0xA6, 0x98, 0x4A, 255),
    "tv_straw_3": (0xCD, 0xBD, 0x66, 255),
    "tv_straw_4": (0xE6, 0xD9, 0x8A, 255),
    "tv_curse_fire_0": (0x2A, 0x1D, 0x3A, 255),
    "tv_curse_fire_1": (0x5A, 0x2D, 0x6B, 255),
    "tv_curse_fire_2": (0x8F, 0x4F, 0xB0, 255),
    "tv_curse_fire_3": (0xC9, 0x8A, 0xE0, 255),
    "tv_curse_fire_4": (0xF2, 0xD1, 0xFF, 255),
    # --- TIERRA VIVA: END ---
    "transparent": (0, 0, 0, 0),
}

## Enmienda 13: significado de las rampas TV (ver gen_tierra_viva_tokens.py).
TV_PURIFIED_ONLY = ['grass', 'leaf', 'flower', 'water', 'eco', 'paramo', 'snow', 'frailejon', 'puya']
TV_SICK_ONLY = ['dry_grass', 'dead_leaf', 'oil', 'sheen', 'sludge', 'smog', 'plastic', 'turbid', 'oil_water', 'plastic_water', 'sludge_grass', 'grey_sand', 'paramo_dry', 'scree', 'sick_soil', 'curse_fire']

## Rampa de calor de la llama, de la brasa apagada al núcleo blanco.
EMBER_RAMP = ["ember_700", "ember_500", "ember_400", "ember_300", "ash_050"]

## Rampa de carbón, del hollín a la ceniza clara.
CHAR_RAMP = ["ash_950", "ash_900", "ash_800", "ash_700", "ash_600"]

## Rampa de la vida que vuelve, para las variantes purificadas. El verde manda:
## la ceniza clara solo asoma como reflejo puntual en el borde iluminado.
VITAL_RAMP = ["vital_900", "vital_700", "vital_700", "vital_500", "ash_200"]


def color(name: str) -> tuple[int, int, int, int]:
    return PALETTE[name]


def ramp(ramp_names: list[str], t: float) -> tuple[int, int, int, int]:
    """Toma el color de una rampa según `t` en [0, 1], sin interpolar.

    Sin interpolación a propósito: el pixel art vive de tener pocos colores
    planos. Mezclarlos produciría una rampa sucia de cientos de tonos.
    """
    index = int(max(0.0, min(0.999, t)) * len(ramp_names))
    return PALETTE[ramp_names[index]]


# --- Ruido determinista ------------------------------------------------------


class ValueNoise:
    """Ruido de valor con interpolación suave, reproducible por semilla."""

    def __init__(self, seed: int, size: int = 64) -> None:
        rng = random.Random(seed)
        self._size = size
        self._grid = [[rng.random() for _ in range(size)] for _ in range(size)]

    def _at(self, ix: int, iy: int) -> float:
        return self._grid[iy % self._size][ix % self._size]

    def sample(self, x: float, y: float) -> float:
        x0, y0 = math.floor(x), math.floor(y)
        fx, fy = x - x0, y - y0
        # Suavizado de Hermite: evita las aristas del ruido bilineal puro.
        sx = fx * fx * (3 - 2 * fx)
        sy = fy * fy * (3 - 2 * fy)
        top = self._at(x0, y0) * (1 - sx) + self._at(x0 + 1, y0) * sx
        bottom = self._at(x0, y0 + 1) * (1 - sx) + self._at(x0 + 1, y0 + 1) * sx
        return top * (1 - sy) + bottom * sy

    def fbm(self, x: float, y: float, octaves: int = 3) -> float:
        """Ruido fractal: varias octavas sumadas, para una silueta orgánica."""
        total, amplitude, frequency, norm = 0.0, 1.0, 1.0, 0.0
        for _ in range(octaves):
            total += self.sample(x * frequency, y * frequency) * amplitude
            norm += amplitude
            amplitude *= 0.5
            frequency *= 2.0
        return total / norm


# --- Lienzo ------------------------------------------------------------------


class Canvas:
    """Lienzo de sprite con acceso por píxel y volcado a PNG."""

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        self.px = self.image.load()

    def set(self, x: int, y: int, rgba: tuple[int, int, int, int]) -> None:
        if 0 <= x < self.width and 0 <= y < self.height and rgba[3] > 0:
            self.px[x, y] = rgba

    def get(self, x: int, y: int) -> tuple[int, int, int, int]:
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.px[x, y]
        return (0, 0, 0, 0)

    def filled(self, x: int, y: int) -> bool:
        return self.get(x, y)[3] > 0

    def rect(self, x: int, y: int, w: int, h: int, rgba) -> None:
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, rgba)

    def outline(self, rgba: tuple[int, int, int, int]) -> None:
        """Contorno de 1 px por fuera de la silueta.

        Da al sprite un borde legible sobre cualquier fondo, que es la razón por
        la que casi todo el pixel art de RPG lo lleva.
        """
        edges: list[tuple[int, int]] = []
        for y in range(self.height):
            for x in range(self.width):
                if self.filled(x, y):
                    continue
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    if self.filled(x + dx, y + dy):
                        edges.append((x, y))
                        break
        for x, y in edges:
            self.set(x, y, rgba)

    def save(self, path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self.image.save(path)
