import os

import pytest

# Set required env vars at module level so the config module can be imported
# during test collection (before any fixtures run).
_TEST_ENV_VARS = {
    "SENDER": "test@example.com",
    "SMTP_SERVER": "smtp.example.com",
    "SMTP_USER": "testuser",
    "SMTP_PWD": "testpass",
    "AZURE_STORAGE_CONNECTION_STRING": "DefaultEndpointsProtocol=https;AccountName=test",
}
for _key, _value in _TEST_ENV_VARS.items():
    os.environ.setdefault(_key, _value)


@pytest.fixture(autouse=True)
def _set_test_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set required env vars for all tests so config module can import."""
    for key, value in _TEST_ENV_VARS.items():
        monkeypatch.setenv(key, value)
