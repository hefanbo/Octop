"""Per-user web-search credentials at call time.

Resolves the caller's personal search keys into the ``tool_env`` mapping the
harness injects for one turn. Only values the user explicitly stored are
included; the harness falls back to the process env for everything else, so an
administrator's global key still works without a personal one.
"""

from __future__ import annotations

from typing import Any

from octop.infra.utils.search_providers import personal_search_providers


def resolve_search_tool_env(*, user_id: int, search_key_repo: Any) -> dict[str, str]:
    """The personal search env for this turn (may be empty).

    Non-user callers (``user_id <= 0``) never get a personal override.
    """
    if user_id <= 0:
        return {}
    out: dict[str, str] = {}
    for spec in personal_search_providers():
        env = search_key_repo.get_env(user_id, spec.id)
        if env:
            out.update(env)
    return out


__all__ = ["resolve_search_tool_env"]
