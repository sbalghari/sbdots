from sbdots.library.configDicts import OneLevelFlatDict


def test_simple_flatten():
    data = {
        "a": {
            "b": 1,
            "c": 2,
        }
    }

    result = OneLevelFlatDict(data)

    assert result == {
        "a": {
            "b": 1,
            "c": 2,
        }
    }


def test_deeply_nested_flatten():
    data = {"a": {"b": {"c": {"d": 1}}}}

    result = OneLevelFlatDict(data)

    assert result == {"a": {"b.c.d": 1}}


def test_multiple_top_level_keys():
    data = {
        "a": {
            "x": 1,
            "y": 2,
        },
        "b": {
            "z": 3,
        },
    }

    result = OneLevelFlatDict(data)

    assert result == {
        "a": {
            "x": 1,
            "y": 2,
        },
        "b": {
            "z": 3,
        },
    }


def test_mixed_value_types():
    data = {
        "a": {
            "b": 1,
            "c": {
                "d": [1, 2, 3],
            },
        },
        "e": "value",
    }

    result = OneLevelFlatDict(data)

    assert result == {
        "a": {
            "b": 1,
            "c.d": [1, 2, 3],
        },
        "e": "value",
    }


def test_non_dict_top_level_value():
    data = {
        "a": 1,
        "b": {
            "c": 2,
        },
    }

    result = OneLevelFlatDict(data)

    assert result == {
        "a": 1,
        "b": {
            "c": 2,
        },
    }


def test_empty_dict():
    result = OneLevelFlatDict({})
    assert result == {}


def test_already_flat_dict_is_unchanged():
    data = {
        "a": {
            "b.c": 1,
            "d": 2,
        }
    }

    result = OneLevelFlatDict(data)

    assert result == data


def test_nested_empty_dict():
    data = {
        "a": {},
        "b": {
            "c": {},
        },
    }

    result = OneLevelFlatDict(data)

    assert result == {
        "a": {},
        "b": {},
    }
