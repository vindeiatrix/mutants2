from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Set, Tuple, Any

from .player import Player, class_key
from .world import World
from . import monsters as monsters_mod
from .types import ItemInstance, ItemListMut, MonsterRec, TileKey
from .state import (
    CharacterProfile,
    apply_profile,
    profile_from_player,
    profile_from_raw,
    profile_to_raw,
)
from .items_util import coerce_item
from .macros import MacroStore

from . import gen

SAVE_SCHEMA = 3


@dataclass
class Save:
    """Metadata stored alongside the world/player state."""

    global_seed: int = gen.SEED
    last_topup_date: str | None = None
    last_class: str | None = None
    profiles: Dict[str, CharacterProfile] = field(default_factory=dict)
    # ``fake_today_override`` is session-only and not persisted
    fake_today_override: str | None = None
    last_upkeep_tick: float = field(default_factory=lambda: time.monotonic())
    next_upkeep_tick: float | None = None  # monotonic deadline for next 10s tick
    max_catchup_ticks: int = 6
    schema: int = SAVE_SCHEMA


SAVE_PATH = Path(os.path.expanduser("~/.mutants2/save.json"))


def _serialize_item(val: ItemInstance | str) -> dict[str, Any]:
    inst = coerce_item(val)
    return {k: v for k, v in inst.items()}


def _deserialize_item(val: Any) -> ItemInstance:
    return coerce_item(val)


def load() -> tuple[
    Player,
    dict[TileKey, ItemListMut],
    dict[TileKey, list[MonsterRec]],
    Set[int],
    Save,
]:
    try:
        with open(SAVE_PATH) as fh:
            data = json.load(fh)
        data.pop("walls", None)
        data.pop("blocked", None)
        if data.get("schema") != SAVE_SCHEMA:
            print("Save schema mismatch; starting with a fresh world.")
            try:
                SAVE_PATH.unlink()
            except FileNotFoundError:
                pass
            raise FileNotFoundError

        profiles: Dict[str, CharacterProfile] = {}
        profiles_raw = data.get("profiles", {})
        if isinstance(profiles_raw, dict):
            for k, v in profiles_raw.items():
                prof = profile_from_raw(v)
                profiles[class_key(k)] = prof

        last_class_raw = data.get("last_class")
        last_class = (
            class_key(last_class_raw) if isinstance(last_class_raw, str) else None
        )
        if last_class not in profiles:
            last_class = None

        active_class: str | None = None
        if last_class:
            active_class = last_class
        elif len(profiles) == 1:
            active_class = next(iter(profiles))

        if active_class:
            prof = profiles[active_class]
            player = Player(year=prof.year, clazz=active_class)
            apply_profile(player, prof)
        else:
            year = int(data.get("year", 2000))
            positions: Dict[int, Tuple[int, int]] = {
                int(k): (v.get("x", 0), v.get("y", 0))
                for k, v in data.get("positions", {}).items()
            }
            clazz = class_key(data.get("class") or "warrior")
            player = Player(year=year, clazz=clazz)
            player.positions.update(positions)
            player.max_hp = int(data.get("max_hp", player.max_hp))
            player.hp = int(data.get("hp", player.max_hp))
            inv_raw = data.get("inventory", [])
            if isinstance(inv_raw, dict):
                for k, v in inv_raw.items():
                    player.inventory.extend([coerce_item(k)] * int(v))
            else:
                for k in inv_raw:
                    player.inventory.append(coerce_item(k))
            player.ions = int(data.get("ions", 0))
            player.riblets = int(data.get("riblets", 0))
            player.level = int(data.get("level", 1))
            player.exp = int(data.get("exp", 0))
            player.strength = int(data.get("strength", 0))
            player.intelligence = int(data.get("intelligence", 0))
            player.wisdom = int(data.get("wisdom", 0))
            player.dexterity = int(data.get("dexterity", 0))
            player.constitution = int(data.get("constitution", 0))
            player.charisma = int(data.get("charisma", 0))
            player.ac = int(data.get("ac", 0))
            player.ready_to_combat_id = data.get("ready_to_combat_id")
            player.ready_to_combat_name = data.get("ready_to_combat_name")
            prof = profile_from_player(player)
            apply_profile(player, prof)
            profiles[clazz] = prof
            last_class = clazz

            macro_dir = MacroStore.MACRO_DIR
            default_macro = macro_dir / "default.json"
            migrated_macro = macro_dir / f"{clazz}.json"
            if default_macro.exists() and not migrated_macro.exists():
                migrated_macro.parent.mkdir(parents=True, exist_ok=True)
                try:
                    default_macro.rename(migrated_macro)
                except Exception:
                    try:
                        import shutil

                        shutil.copy(default_macro, migrated_macro)
                    except Exception:
                        pass

        ground: dict[TileKey, ItemListMut] = {}
        for key, val in data.get("ground", {}).items():
            parts = [int(n) for n in key.split(",")]
            coord: TileKey = (parts[0], parts[1], parts[2])
            if isinstance(val, list):
                ground[coord] = [_deserialize_item(v) for v in val]
            else:
                ground[coord] = [_deserialize_item(val)]
        monsters_data: dict[TileKey, list[MonsterRec]] = {}
        for key, val in data.get("monsters", {}).items():
            parts = [int(n) for n in key.split(",")]
            coord: TileKey = (parts[0], parts[1], parts[2])
            entries = val if isinstance(val, list) else [val]
            lst: list[MonsterRec] = []
            for entry in entries:
                m_key = entry.get("key")
                if m_key is None:
                    continue
                hp = entry.get("hp")
                name = entry.get("name")
                aggro = entry.get("aggro", False)
                seen = entry.get("seen", False)
                has_yelled = entry.get("yelled_once") or entry.get(
                    "has_yelled_this_aggro", False
                )
                mid = entry.get("id")
                loot_i = entry.get("loot_ions", 0)
                loot_r = entry.get("loot_riblets", 0)
                base = monsters_mod.REGISTRY[m_key].base_hp
                m: dict[str, object] = {
                    "key": m_key,
                    "hp": int(hp) if hp is not None else base,
                    "name": name or monsters_mod.REGISTRY[m_key].name,
                    "aggro": bool(aggro),
                    "seen": bool(seen),
                    "yelled_once": bool(has_yelled),
                    "loot_ions": int(loot_i),
                    "loot_riblets": int(loot_r),
                }
                if mid is not None:
                    m["id"] = int(mid)
                if m.get("aggro") and not m.get("seen"):
                    m["aggro"] = False
                if not m.get("aggro"):
                    m["yelled_once"] = False
                lst.append(m)
            if lst:
                monsters_data[coord] = lst
        seeded = {int(y) for y in data.get("seeded_years", [])}
        last_wall = float(
            data.get("last_upkeep_tick", data.get("last_ion_tick", time.time()))
        )
        now_wall = time.time()
        save_meta = Save(
            global_seed=int(data.get("global_seed", gen.SEED)),
            last_topup_date=data.get("last_topup_date"),
            last_class=last_class,
            profiles=profiles,
            last_upkeep_tick=time.monotonic() - max(0.0, now_wall - last_wall),
            max_catchup_ticks=int(data.get("max_catchup_ticks", 6)),
            schema=int(data.get("schema", 1)),
        )

        from .items_resolver import resolve_key

        def _migrate_list(lst):
            out = []
            for it in lst:
                inst = coerce_item(it)
                inst["key"] = resolve_key(inst["key"])
                out.append(inst)
            return out

        player.inventory = _migrate_list(player.inventory)
        if player.worn_armor is not None:
            player.worn_armor = coerce_item(player.worn_armor)
            player.worn_armor["key"] = resolve_key(player.worn_armor["key"])
        for k, items in ground.items():
            ground[k] = _migrate_list(items)

        return player, ground, monsters_data, seeded, save_meta
    except FileNotFoundError:
        player = Player()
        ground: dict[TileKey, ItemListMut] = {}
        monsters_data: dict[TileKey, list[MonsterRec]] = {}
        seeded: Set[int] = set()
        save_meta = Save()
        save(
            player,
            World(
                ground,
                seeded,
                monsters_data,
                seed_monsters=False,
                global_seed=save_meta.global_seed,
            ),
            save_meta,
        )
        return player, ground, monsters_data, seeded, save_meta


def save(player: Player, world: World, save_meta: Save) -> None:
    SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)
    if player.clazz:
        k = class_key(player.clazz)
        save_meta.profiles[k] = profile_from_player(player)
        save_meta.last_class = k
    with open(SAVE_PATH, "w") as fh:
        data = {
            "year": player.year,
            "positions": {
                str(y): {"x": x, "y": yy} for y, (x, yy) in player.positions.items()
            },
            "class": player.clazz,
            "hp": player.hp,
            "max_hp": player.max_hp,
            "level": player.level,
            "exp": player.exp,
            "inventory": [_serialize_item(i) for i in player.inventory],
            "ions": player.ions,
            "riblets": getattr(player, "riblets", 0),
            "strength": player.strength,
            "intelligence": player.intelligence,
            "wisdom": player.wisdom,
            "dexterity": player.dexterity,
            "constitution": player.constitution,
            "charisma": player.charisma,
            "ac": player.ac,
            "ready_to_combat_id": player.ready_to_combat_id,
            "ready_to_combat_name": player.ready_to_combat_name,
            "profiles": {
                k: profile_to_raw(v) if isinstance(v, CharacterProfile) else v
                for k, v in save_meta.profiles.items()
            },
            "last_class": save_meta.last_class,
            "last_upkeep_tick": (
                time.time() - (time.monotonic() - save_meta.last_upkeep_tick)
            ),
            "max_catchup_ticks": save_meta.max_catchup_ticks,
            "ground": {
                f"{y},{x},{yy}": (
                    _serialize_item(items[0])
                    if len(items) == 1
                    else [_serialize_item(i) for i in items]
                )
                for (y, x, yy), items in world.ground.items()
            },
            "monsters": {
                f"{y},{x},{yy}": (processed[0] if len(processed) == 1 else processed)
                for (y, x, yy), lst in world.monsters.items()
                for processed in [
                    [
                        {
                            "key": m["key"],
                            "hp": m["hp"],
                            "name": m.get("name"),
                            "aggro": m.get("aggro", False),
                            "seen": m.get("seen", False),
                            "yelled_once": m.get("yelled_once", False),
                            "id": m.get("id"),
                            "loot_ions": m.get("loot_ions", 0),
                            "loot_riblets": m.get("loot_riblets", 0),
                        }
                        for m in lst
                    ]
                ]
            },
            "seeded_years": list(world.seeded_years),
            "global_seed": save_meta.global_seed,
            "last_topup_date": save_meta.last_topup_date,
            "schema": save_meta.schema,
            # no senses data; cues are never persisted
        }
        json.dump(data, fh)
