import sys

import pytest

from pygate.settings import get_settings


class TestGetSettingsDefaults:
    def test_no_args_no_env_uses_field_defaults(self):
        settings = get_settings()
        assert settings.host == "0.0.0.0"
        assert settings.port == 8080


class TestGetSettingsCliOverrides:
    def test_cli_host_and_port_override_defaults(self, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["pygate", "--host", "5.5.5.5", "--port", "4321"])
        settings = get_settings()
        assert settings.host == "5.5.5.5"
        assert settings.port == 4321

    def test_cli_env_file_is_loaded(self, monkeypatch, env_file):
        path = env_file(host="10.0.0.1", port="1234")
        monkeypatch.setattr(sys, "argv", ["pygate", "--env-file", path])
        settings = get_settings()
        assert settings.host == "10.0.0.1"
        assert settings.port == 1234


class TestGetSettingsEnvVarFallback:
    def test_pygate_env_file_var_used_when_no_cli_flag(self, monkeypatch, env_file):
        path = env_file(host="10.0.0.1", port="1234")
        monkeypatch.setenv("PYGATE_ENV_FILE", path)
        settings = get_settings()
        assert settings.host == "10.0.0.1"
        assert settings.port == 1234

    def test_cli_flag_takes_priority_over_env_var(self, monkeypatch, env_file):
        env_file_path = env_file(host="1.1.1.1", port="1111")
        cli_file_path = env_file(host="2.2.2.2", port="2222")
        monkeypatch.setenv("PYGATE_ENV_FILE", env_file_path)
        monkeypatch.setattr(sys, "argv", ["pygate", "--env-file", cli_file_path])
        settings = get_settings()
        assert settings.host == "2.2.2.2"
        assert settings.port == 2222


class TestGetSettingsExplicitArgPriority:
    def test_explicit_function_arg_wins_over_pygate_env_file_var(self, monkeypatch, env_file):
        explicit_path = env_file(host="3.3.3.3", port="3333")
        monkeypatch.setenv("PYGATE_ENV_FILE", "should-be-ignored.env")

        settings = get_settings(env_file=explicit_path)

        assert settings.host == "3.3.3.3"
        assert settings.port == 3333

    def test_process_env_still_overrides_explicit_env_file(self, monkeypatch, env_file):
        explicit_path = env_file(host="3.3.3.3", port="3333")
        monkeypatch.setenv("PYGATE_HOST", "8.8.8.8")

        settings = get_settings(env_file=explicit_path)

        assert settings.host == "8.8.8.8"
        assert settings.port == 3333

    def test_explicit_env_file_does_not_skip_cli_field_parsing(self, monkeypatch, env_file):
        explicit_path = env_file(host="3.3.3.3", port="3333")
        monkeypatch.setattr(sys, "argv", ["pygate", "--host", "9.9.9.9"])

        settings = get_settings(env_file=explicit_path)

        assert settings.host == "9.9.9.9"

    def test_explicit_env_file_with_unrelated_cli_env_file_flag_raises(
        self, monkeypatch, env_file
    ):
        explicit_path = env_file(host="3.3.3.3", port="3333")
        cli_path = env_file(host="4.4.4.4", port="4444")
        monkeypatch.setattr(sys, "argv", ["pygate", "--env-file", cli_path])

        with pytest.raises(SystemExit):
            get_settings(env_file=explicit_path)
