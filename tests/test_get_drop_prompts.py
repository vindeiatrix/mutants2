def test_get_without_arg_prompts(cli_runner):
    out = cli_runner.run_commands(["get"])
    assert "What do you want to get?" in out
    # Should not render room or list inventory/ground here
    after = out.split("What do you want to get?", 1)[1]
    assert "***" not in after and "On the ground" not in after


def test_drop_without_arg_prompts(cli_runner):
    out = cli_runner.run_commands(["dro"])
    assert "What do you want to drop?" in out
    after = out.split("What do you want to drop?", 1)[1]
    assert "***" not in after and "Inventory:" not in after

