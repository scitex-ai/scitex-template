"""Refresh a real local Git cache; changing defaults must not serve main."""

import subprocess

import pytest

from scitex_template import _cache


def git(repository, *arguments):
    return subprocess.check_output(
        ["git", "-C", str(repository), *arguments], text=True, stderr=subprocess.DEVNULL
    ).strip()


@pytest.fixture
def local_remote(tmp_path):
    remote = tmp_path / "remote"
    remote.mkdir()
    git(remote, "init", "-b", "main")
    (remote / "payload").write_text("main content")
    git(remote, "add", ".")
    git(
        remote,
        "-c",
        "user.name=Test",
        "-c",
        "user.email=test@example.org",
        "commit",
        "-m",
        "main",
    )
    git(remote, "checkout", "-b", "develop")
    (remote / "payload").write_text("develop content")
    git(remote, "add", ".")
    git(
        remote,
        "-c",
        "user.name=Test",
        "-c",
        "user.email=test@example.org",
        "commit",
        "-m",
        "develop",
    )
    previous_root, previous_url = _cache.CACHE_ROOT, _cache.MONOREPO_URL
    _cache.CACHE_ROOT = tmp_path / "cache"
    _cache.MONOREPO_URL = remote.as_uri()
    try:
        yield remote
    finally:
        _cache.CACHE_ROOT, _cache.MONOREPO_URL = previous_root, previous_url


def test_existing_main_cache_switches_to_current_develop(local_remote):
    cache = _cache.ensure_cache(branch="main")
    assert (cache / "payload").read_text() == "main content"
    _cache.ensure_cache()
    assert (cache / "payload").read_text() == "develop content"
    assert git(cache, "branch", "--show-current") == "develop"
    assert git(cache, "rev-parse", "HEAD") == git(local_remote, "rev-parse", "develop")


def test_failed_refresh_reports_staleness_without_erasing_cache(local_remote):
    cache = _cache.ensure_cache()
    local_remote.rename(local_remote.with_name("unavailable"))
    with pytest.raises(RuntimeError, match="failed to refresh"):
        _cache.ensure_cache()
    assert (cache / "payload").read_text() == "develop content"
