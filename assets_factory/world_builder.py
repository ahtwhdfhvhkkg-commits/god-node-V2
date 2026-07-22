"""
assets_factory/world_builder.py

Procedural Asset & World Generation Engine for God Node.
Dynamically spawns terrain, items, and structures without hardcoding.
यह फाइल गेम की दुनिया (मैप, आइटम्स, स्ट्रक्चर्स) को डायनामिक तरीके से बनाती है।
"""

import uuid
import random
from typing import Dict, Any, List
from dataclasses import dataclass, field

@dataclass
class AssetBlueprint:
    """किसी भी 3D चीज़ (हथियार, बिल्डिंग, पेड़) का कच्चा ढांचा (Blueprint)"""
    asset_id: str
    asset_type: str  # उदाहरण: "TERRAIN", "WEAPON", "BUILDING", "VEHICLE"
    coordinates: tuple[float, float, float] # 3D दुनिया में X, Y, Z पोजीशन
    properties: Dict[str, Any] = field(default_factory=dict)

class ProceduralWorldBuilder:
    def __init__(self, seed: int = 42):
        self.seed = seed
        random.seed(self.seed)
        # मेमोरी में सेव्ड सारे एक्टिव 3D एसेट्स
        self.active_assets: Dict[str, AssetBlueprint] = {}
        print(f"[ASSETS FACTORY] World Builder initialized with Seed: {self.seed}")

    def generate_terrain_chunk(self, chunk_x: int, chunk_y: int, chunk_size: int = 100) -> List[AssetBlueprint]:
        """हवा में तुरंत ज़मीन (Terrain/Map) का एक हिस्सा (Chunk) बनाना"""
        generated_assets = []
        
        # बेस ज़मीन (Base Ground) जनरेट करना
        ground_id = f"terrain_{chunk_x}_{chunk_y}_{uuid.uuid4().hex[:6]}"
        ground = AssetBlueprint(
            asset_id=ground_id,
            asset_type="TERRAIN",
            coordinates=(chunk_x * chunk_size, 0.0, chunk_y * chunk_size),
            properties={"biome": "default", "size": chunk_size}
        )
        self.active_assets[ground_id] = ground
        generated_assets.append(ground)

        # रैंडम पेड़, पत्थर या प्रॉप्स स्पॉन (Spawn) करना
        for _ in range(random.randint(5, 15)):
            prop_id = f"prop_{uuid.uuid4().hex[:8]}"
            offset_x = random.uniform(-chunk_size/2, chunk_size/2)
            offset_z = random.uniform(-chunk_size/2, chunk_size/2)
            
            prop = AssetBlueprint(
                asset_id=prop_id,
                asset_type="ENVIRONMENT_PROP",
                coordinates=(chunk_x * chunk_size + offset_x, 0.0, chunk_y * chunk_size + offset_z),
                properties={"type": random.choice(["tree", "rock", "bush"]), "scale": random.uniform(0.8, 1.5)}
            )
            self.active_assets[prop_id] = prop
            generated_assets.append(prop)

        return generated_assets

    def spawn_item(self, item_name: str, location: tuple[float, float, float], attributes: dict) -> AssetBlueprint:
        """गेम में कोई भी रैंडम आइटम (जैसे बंदूक, हेल्थ किट) स्पॉन करना"""
        item_id = f"item_{item_name}_{uuid.uuid4().hex[:8]}"
        new_item = AssetBlueprint(
            asset_id=item_id,
            asset_type="ITEM",
            coordinates=location,
            properties=attributes
        )
        self.active_assets[item_id] = new_item
        print(f"[ASSETS FACTORY] Spawned {item_name} at {location}")
        return new_item

    def clear_world(self):
        """अगर गेम क्रैश हो या रीस्टार्ट करना हो, तो पूरी 3D दुनिया मिटा देना"""
        self.active_assets.clear()
        print("[ASSETS FACTORY] World memory wiped clean.")

# ग्लोबल इंस्टेंस जिसे हम पूरे सर्वर में कहीं भी इस्तेमाल करेंगे
world_forge = ProceduralWorldBuilder()
