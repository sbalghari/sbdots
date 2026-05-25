import pytest

from sbdots.library.configDicts import ConfigResolvedDict, _PLACEHOLDER_RE


BASE_CONFIG = {
    "env": {
        "name": "prod",
        "debug": False,
        "ports": {
            "http": 80,
            "https": 443,
        },
        "paths": {
            "home": "/srv/app",
            "logs": "/var/log/app",
        },
    },
    "db": {
        "host": "localhost",
        "port": 5432,
        "credentials": {
            "user": "admin",
            "password": "secret",
        },
    },
}

SUCCESS_CONFIG = {
    **BASE_CONFIG,
    # full placeholder → type preserved
    "http_port": "{env.ports.http}",
    "debug_mode": "{env.debug}",
    "db_port": "{db.port}",
    # string interpolation
    "db_url": "postgres://{db.credentials.user}:{db.credentials.password}@{db.host}:{db.port}/app",
    "log_path": "{env.paths.logs}/{env.name}.log",
    # nested dicts
    "service": {
        "name": "api-{env.name}",
        "bind": "0.0.0.0:{env.ports.http}",
        "paths": {
            "root": "{env.paths.home}",
            "logs": "{env.paths.logs}",
        },
    },
    # lists
    "allowed_ports": [
        "{env.ports.http}",
        "{env.ports.https}",
        8080,
        "static",
    ],
    "servers": [
        {
            "name": "primary",
            "host": "{db.host}",
            "port": "{db.port}",
        },
        {
            "name": "secondary",
            "host": "replica.local",
            "port": "{db.port}",
        },
    ],
}


def test_resolves_successfully():
    cfg = ConfigResolvedDict(SUCCESS_CONFIG)
    assert isinstance(cfg, dict)


def test_raw_is_preserved():
    cfg = ConfigResolvedDict(SUCCESS_CONFIG)
    assert cfg.raw is SUCCESS_CONFIG


def test_full_placeholder_preserves_type():
    cfg = ConfigResolvedDict(SUCCESS_CONFIG)

    assert cfg["http_port"] == 80
    assert isinstance(cfg["http_port"], int)

    assert cfg["debug_mode"] is False
    assert isinstance(cfg["debug_mode"], bool)


def test_string_interpolation():
    cfg = ConfigResolvedDict(SUCCESS_CONFIG)

    assert cfg["db_url"] == ("postgres://admin:secret@localhost:5432/app")


def test_nested_resolution():
    cfg = ConfigResolvedDict(SUCCESS_CONFIG)

    assert cfg["service"]["name"] == "api-prod"
    assert cfg["service"]["paths"]["root"] == "/srv/app"


def test_list_resolution():
    cfg = ConfigResolvedDict(SUCCESS_CONFIG)

    assert cfg["allowed_ports"] == [80, 443, 8080, "static"]


def test_list_of_dicts_resolution():
    cfg = ConfigResolvedDict(SUCCESS_CONFIG)

    servers = cfg["servers"]
    assert servers[0]["host"] == "localhost"
    assert servers[1]["host"] == "replica.local"
    assert servers[0]["port"] == 5432


def test_no_placeholder_returns_original_string():
    cfg = ConfigResolvedDict({"env": {}, "value": "plain"})
    assert cfg["value"] == "plain"


def test_placeholder_regex_matches_expected():
    assert _PLACEHOLDER_RE.search("{env.name}")
    assert _PLACEHOLDER_RE.fullmatch("{env.name}")


def test_unknown_mapping_dict_raises_key_error():
    with pytest.raises(KeyError, match="Unknown mapping dict"):
        ConfigResolvedDict(
            {
                **BASE_CONFIG,
                "value": "{missing.key}",
            }
        )


def test_missing_top_level_key_raises_key_error():
    with pytest.raises(KeyError, match="Invalid key"):
        ConfigResolvedDict(
            {
                **BASE_CONFIG,
                "value": "{env.nope}",
            }
        )


def test_missing_nested_key_raises_key_error():
    with pytest.raises(KeyError, match="Key 'missing' not found"):
        ConfigResolvedDict(
            {
                **BASE_CONFIG,
                "value": "{env.ports.missing}",
            }
        )


def test_non_dict_root_raises_type_error():
    with pytest.raises(TypeError, match="Expected dict"):
        ConfigResolvedDict(
            {
                "env": "not-a-dict",
                "value": "{env.name}",
            }
        )


def test_non_dict_mid_path_raises_type_error():
    with pytest.raises(TypeError):
        ConfigResolvedDict(
            {
                **BASE_CONFIG,
                "value": "{env.name.value}",
            }
        )
