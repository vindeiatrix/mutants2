def test_digit_resolves_to_keypad_alias():
    from mutants2.engine.macros import MacroStore, resolve_bound_script

    store = MacroStore()
    store.bind("kp4", "west")
    assert resolve_bound_script(store, "4") == "west"
