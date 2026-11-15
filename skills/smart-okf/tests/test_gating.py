"""Tests for ingest gating (exclude / deprioritize decisions)."""

from app.services.gating import GatingRules, is_deprioritized, is_excluded


def test_exclude_matches_bare_filename_and_full_path() -> None:
    rules = GatingRules(exclude_patterns=["*handbuch*", "manuals/*"])
    assert is_excluded("providers/router-handbuch.pdf", rules)
    assert is_excluded("manuals/anything.pdf", rules)
    assert not is_excluded("providers/contract.pdf", rules)


def test_no_patterns_excludes_nothing() -> None:
    assert not is_excluded("providers/contract.pdf", GatingRules())


def test_trivial_keyword_deprioritizes_eagerly_without_any_pattern() -> None:
    # No user patterns at all, but a built-in trivial keyword still deprioritizes.
    assert is_deprioritized("providers/AGB_2024.pdf", GatingRules())
    assert is_deprioritized("insurance/widerrufsbelehrung.pdf", GatingRules())


def test_normal_document_is_not_deprioritized() -> None:
    assert not is_deprioritized("finances/kontoauszug-2024.pdf", GatingRules())


def test_low_priority_pattern_deprioritizes() -> None:
    rules = GatingRules(low_priority_patterns=["archive/*"])
    assert is_deprioritized("archive/old.pdf", rules)


def test_priority_pattern_overrides_trivial_keyword_and_low_priority() -> None:
    rules = GatingRules(
        low_priority_patterns=["*.pdf"],
        priority_patterns=["*wichtig*"],
    )
    # Would be low-priority by pattern and even trivial by keyword, but priority wins.
    assert not is_deprioritized("legal/wichtig-agb-vertrag.pdf", rules)


def test_exclude_is_independent_of_deprioritize() -> None:
    # A file can be deprioritized (trivial) without being excluded — it is still ingested.
    rules = GatingRules()
    assert not is_excluded("providers/AGB.pdf", rules)
    assert is_deprioritized("providers/AGB.pdf", rules)


def test_local_only_blocks_only_when_llm_is_remote() -> None:
    from app.services.gating import is_blocked_for_remote

    remote = GatingRules(local_only_patterns=["health/*"], remote_llm=True)
    local = GatingRules(local_only_patterns=["health/*"], remote_llm=False)
    assert is_blocked_for_remote("health/visits/report.pdf", remote)
    assert not is_blocked_for_remote("health/visits/report.pdf", local)


def test_local_only_matches_folder_glob_and_nothing_else() -> None:
    from app.services.gating import is_blocked_for_remote

    rules = GatingRules(local_only_patterns=["health/*"], remote_llm=True)
    assert is_blocked_for_remote("health/report.pdf", rules)
    assert not is_blocked_for_remote("finances/report.pdf", rules)
    assert not is_blocked_for_remote("health/report.pdf", GatingRules(remote_llm=True))
