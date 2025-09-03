from .world import World
from .player import Player
from .senses import SensesCues
from ..render import render_room_at


def shadow_lines(world: World, player: Player) -> list[str]:
    ds = world.shadow_dirs(player.year, player.x, player.y)
    return [f"You see shadows to the {', '.join(ds)}."] if ds else []


def entry_yell_lines(ctx) -> list[str]:
    lines = getattr(ctx, "_entry_yells", []) or []
    ctx._entry_yells = []
    return lines


def arrival_lines(ctx) -> list[str]:
    msgs = getattr(ctx, "_arrivals_this_tick", []) or []
    ctx._arrivals_this_tick = []
    return msgs


def footsteps_lines(ctx) -> list[str]:
    ev = getattr(ctx, "_footsteps_event", None)
    ctx._footsteps_event = None
    if not ev:
        return []
    kind, d = ev
    if kind == "faint":
        return [f"You hear faint sounds of footsteps far to the {d}."]
    else:
        return [f"You hear loud sounds of footsteps to the {d}."]


def render_room_view(player: Player, world: World, context=None, *, consume_cues: bool = True) -> None:
    if consume_cues:
        cues = player.senses.pop()
    else:
        cues = SensesCues()
    text = render_room_at(
        world,
        player.year,
        player.x,
        player.y,
        include_shadows=True,
        shadow_dirs_extra=cues.shadow_dirs,
    )
    print(text)


# Backwards compatibility
render = render_room_view
