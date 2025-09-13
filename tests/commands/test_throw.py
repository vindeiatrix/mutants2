def test_throw_invalid_item_graceful(ctx):
    ctx.player["inventory"] = []

    # should not raise an error
    try:
        throw.throw_cmd("not-a-real-item n", ctx)
    except Exception as e:
        assert False, f"throw_cmd crashed: {e}"

    # expected to push a warning or message to bus/log
    # (replace with your actual message bus assertion)
    # e.g., assert "SYSTEM/WARN" in [e.kind for e in ctx.bus.events]
def test_throw_abbreviation_unique(ctx):
    # put two items in inventory, one starts with 'ion'
    ion_item = items_instances.create_and_save_instance("ion-decay")
    ctx.player["inventory"] = [ion_item["iid"]]

    # abbreviation 'i' should resolve to ion-decay
    throw.throw_cmd("i n", ctx)

    # should no longer be in inventory
    assert ion_item["iid"] not in ctx.player["inventory"]
