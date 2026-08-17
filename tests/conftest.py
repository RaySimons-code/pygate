import sys

import pytest

@pytest.fixture(autouse=True)
def isolated_config_env(monkeypatch, tmp_path):
    for key in list(dict(__import__("os").environ)):
        if key.startswith("PYGATE_"):
            monkeypatch.delenv(key, raising=False)

    monkeypatch.setattr(sys, "argv", ["pygate"])
    monkeypatch.chdir(tmp_path)

    yield


@pytest.fixture
def env_file(tmp_path):
    """Write a .env-style file and return its path."""

    def _make(**pairs: str) -> str:
        path = tmp_path / "custom.env"
        content = "\n".join(f"PYGATE_{k.upper()}={v}" for k, v in pairs.items())
        path.write_text(content + "\n")
        return str(path)

    return _make
