"""Per-turn resolution of personal search credentials."""

from __future__ import annotations

from typing import Any

from octop.infra.agents.providers.search_keys import resolve_search_tool_env


class _FakeRepo:
    def __init__(self, stored: dict[tuple[int, str], dict[str, str]]) -> None:
        self._stored = stored

    def get_env(self, user_id: int, provider_id: str) -> dict[str, str] | None:
        return self._stored.get((user_id, provider_id))


def test_returns_only_user_configured_values() -> None:
    repo = _FakeRepo(
        {
            (7, "deepseek"): {"DEEPSEEK_API_KEY": "sk-deepseek"},
            (7, "google"): {"GOOGLE_API_KEY": "g-key", "GOOGLE_CSE_ID": "g-cse"},
        }
    )
    env = resolve_search_tool_env(user_id=7, search_key_repo=repo)
    assert env == {
        "DEEPSEEK_API_KEY": "sk-deepseek",
        "GOOGLE_API_KEY": "g-key",
        "GOOGLE_CSE_ID": "g-cse",
    }


def test_no_stored_keys_returns_empty_for_global_fallback() -> None:
    assert resolve_search_tool_env(user_id=7, search_key_repo=_FakeRepo({})) == {}


def test_keys_are_per_user() -> None:
    repo = _FakeRepo({(8, "deepseek"): {"DEEPSEEK_API_KEY": "sk-eight"}})
    assert resolve_search_tool_env(user_id=7, search_key_repo=repo) == {}
    assert resolve_search_tool_env(user_id=8, search_key_repo=repo) == {
        "DEEPSEEK_API_KEY": "sk-eight"
    }


def test_non_user_callers_never_get_overrides() -> None:
    class _ExplodingRepo:
        def get_env(self, *_args: Any) -> dict[str, str] | None:  # pragma: no cover
            raise AssertionError("must not read personal keys for non-user callers")

    assert resolve_search_tool_env(user_id=0, search_key_repo=_ExplodingRepo()) == {}
    assert resolve_search_tool_env(user_id=-1, search_key_repo=_ExplodingRepo()) == {}
