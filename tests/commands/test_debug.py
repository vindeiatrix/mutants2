from mutants.commands import debug
from mutants.bus import Bus

def test_debug_add_item_rejects_invalid(monkeypatch):
    bus = Bus()
    player = {}
    calls = []

    # capture bus pushes
    bus.push = lambda kind, payload=None: calls.append((kind, payload))

    # run command with invalid item
    debug.cmd_debug_add_item(bus, player, ["INVALID_ITEM_ID"])

    # should have warned instead of adding
    kinds = [c[0] for c in calls]
    assert "SYSTEM/WARN" in kinds
    assert not any(k.startswith("PLAYER/ITEM/ADD") for k in kinds)
