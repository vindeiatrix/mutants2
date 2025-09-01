from mutants2.cli.keynames import normalize_key
from mutants2.engine.macros import MacroStore, resolve_bound_script


def test_normalize_key_aliases():
    assert normalize_key("kp4") == "kp4"
    assert normalize_key("F5") == "f5"
    assert normalize_key("z") == "z"


def test_keypad_fallback_resolve():
    store = MacroStore()
    store.bind("kp4", "look")
    assert resolve_bound_script(store, "4") == "look"
