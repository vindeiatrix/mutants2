import contextlib
import io
from types import SimpleNamespace

from mutants2.engine import loop, world as world_mod, persistence
from mutants2.engine.player import Player


class FakeTime:
    def __init__(self):
        self.now = 0.0

    def monotonic(self) -> float:  # pragma: no cover - simple helper
        return self.now


def test_scheduler_and_gating(monkeypatch):
    fake = FakeTime()
    monkeypatch.setattr(loop, "time", fake)

    p = Player(year=2000, clazz="Warrior", level=6, ions=0, hp=30, max_hp=30)
    w = world_mod.World(global_seed=1)
    save = persistence.Save(global_seed=1)
    ctx = SimpleNamespace(player=p, world=w, in_game=False, tick_handle=None)

    save.next_upkeep_tick = 0.0
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        loop.maybe_process_upkeep(p, w, save, ctx, now=fake.monotonic())
    assert p.hp == 30
    assert save.next_upkeep_tick == 0.0

    ctx.in_game = True
    with contextlib.redirect_stdout(buf):
        loop.maybe_process_upkeep(p, w, save, ctx, now=fake.monotonic())
    assert p.hp == 24
    assert save.next_upkeep_tick == 10.0

    for t in range(1, 10):
        fake.now = t
        loop.maybe_process_upkeep(p, w, save, ctx)
    assert p.hp == 24

    fake.now = 10
    loop.maybe_process_upkeep(p, w, save, ctx)
    assert p.hp == 18
    assert save.next_upkeep_tick == 20.0

    fake.now = 60
    loop.maybe_process_upkeep(p, w, save, ctx)
    assert p.hp == 12
    assert save.next_upkeep_tick == 70.0

    ctx.tick_handle = object()
    fake.now = 70
    loop.maybe_process_upkeep(p, w, save, ctx)
    assert p.hp == 12


def test_start_realtime_tick_single_thread(monkeypatch):
    p = Player(year=2000, clazz="Warrior")
    w = world_mod.World(global_seed=1)
    save = persistence.Save(global_seed=1)
    ctx = SimpleNamespace(player=p, world=w, in_game=True, tick_handle=None)

    calls: list[int] = []

    class DummyThread:
        def __init__(self, *a, **kw):
            calls.append(1)

        def start(self) -> None:  # pragma: no cover - no-op
            pass

        def join(self, timeout=None) -> None:  # pragma: no cover - no-op
            pass

    monkeypatch.setattr(loop.threading, "Thread", DummyThread)

    handle1 = loop.start_realtime_tick(p, w, save, ctx)
    ctx.tick_handle = handle1
    assert len(calls) == 1

    handle2 = loop.start_realtime_tick(p, w, save, ctx)
    assert handle2 is handle1
    assert len(calls) == 1

    loop.stop_realtime_tick(handle1)
