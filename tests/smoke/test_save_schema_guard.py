from mutants2.engine.persistence import SAVE_SCHEMA


def test_save_schema_guard():
    assert SAVE_SCHEMA == 6
