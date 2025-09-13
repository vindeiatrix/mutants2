from mutants.commands import throw
from mutants.state import items_instances, items_ground

def test_throw_places_item_on_ground(ctx):
    # create an item in inventory
    instance = items_instances.create_and_save_instance("ion-decay")
    ctx.player["inventory"] = [instance["iid"]]

    # throw north (assume tile (0,0) with exit north → (0,1))
    throw.throw_cmd("ion-decay n", ctx)

    # item should no longer be in inventory
    assert instance["iid"] not in ctx.player["inventory"]

    # item should appear on ground in destination tile
    ground_items = items_ground.load((ctx.year, ctx.pos[0], ctx.pos[1] + 1))
    assert any(i["iid"] == instance["iid"] for i in ground_items)
