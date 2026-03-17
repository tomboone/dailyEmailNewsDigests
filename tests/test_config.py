import importlib

import pytest


def test_missing_required_env_var_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    """Config module raises RuntimeError if a required env var is missing."""
    import src.dailyemailnewsdigests.config as config_module  # ensure module is loaded first

    monkeypatch.delenv("SENDER", raising=False)
    with pytest.raises(RuntimeError, match="SENDER"):
        importlib.reload(config_module)


def test_optional_vars_have_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    """Optional config vars use defaults when not set."""
    monkeypatch.delenv("DIGEST_NAME", raising=False)
    monkeypatch.delenv("SMTP_PORT", raising=False)
    import src.dailyemailnewsdigests.config as config_module

    importlib.reload(config_module)
    assert config_module.DIGEST_NAME == "News Digest"
    assert config_module.SMTP_PORT == 587
