"""Refresh behaviour of ``scitex_template._cache.ensure_cache`` (issue #81).

Real git end to end, no fakes: a local repository stands in for the
monorepo remote. ``CACHE_ROOT`` and ``MONOREPO_URL`` are module attributes,
swapped and restored by hand (PA-306: no monkeypatch, no mock).

Issue #81: a failed refresh silently served an 11-week-old cached template.
A refresh failure must now raise, naming the cached commit; using the cache
without a refresh is an explicit ``offline=True`` opt-in.
"""

import shutil
import subprocess
import warnings
from pathlib import Path

import pytest
from scitex_template import _cache


def _git(cwd: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(cwd), *args], check=True, capture_output=True, text=True
    ).stdout.strip()


def _commit(repo: Path, text: str) -> str:
    (repo / "templates").mkdir(exist_ok=True)
    (repo / "templates" / "VERSION").write_text(text)
    _git(repo, "add", "-A")
    _git(
        repo,
        "-c",
        "user.name=t",
        "-c",
        "user.email=t@example.invalid",
        "commit",
        "-q",
        "-m",
        text,
    )
    return _git(repo, "rev-parse", "HEAD")


def _raised(call):
    """Run ``call``; return the exception it raised, or ``None``."""
    try:
        call()
    except Exception as exc:  # noqa: BLE001 - the test inspects it
        return exc
    return None


@pytest.fixture
def remote_and_cache(tmp_path):
    """A local 'monorepo' with main + develop, wired as the cache's remote."""
    remote = tmp_path / "remote"
    remote.mkdir()
    _git(remote, "init", "-q", "-b", "main")
    _commit(remote, "v1")
    _git(remote, "branch", "develop")
    cache = tmp_path / "cache"
    saved = (_cache.CACHE_ROOT, _cache.MONOREPO_URL)
    _cache.CACHE_ROOT = cache
    _cache.MONOREPO_URL = remote.as_uri()
    try:
        yield remote, cache
    finally:
        _cache.CACHE_ROOT, _cache.MONOREPO_URL = saved


@pytest.fixture
def stale_cache(remote_and_cache):
    """A populated cache whose remote has since become unreachable."""
    remote, cache = remote_and_cache
    _cache.ensure_cache()
    shutil.rmtree(remote)
    return cache


def test_first_call_clones_the_branch(remote_and_cache):
    # Arrange
    _remote, cache = remote_and_cache
    # Act
    _cache.ensure_cache()
    # Assert
    assert (cache / "templates" / "VERSION").read_text() == "v1"


def test_refresh_moves_existing_cache_to_the_new_tip(remote_and_cache):
    # Arrange
    remote, cache = remote_and_cache
    _cache.ensure_cache()
    tip = _commit(remote, "v2")
    # Act
    _cache.ensure_cache()
    # Assert
    assert (
        _git(cache, "rev-parse", "HEAD"),
        (cache / "templates" / "VERSION").read_text(),
    ) == (tip, "v2")


def test_refresh_switches_branch(remote_and_cache):
    # Arrange
    remote, cache = remote_and_cache
    _cache.ensure_cache(branch="main")
    _git(remote, "checkout", "-q", "develop")
    _commit(remote, "dev")
    _git(remote, "checkout", "-q", "main")
    # Act
    _cache.ensure_cache(branch="develop")
    # Assert
    assert (cache / "templates" / "VERSION").read_text() == "dev"


def test_refresh_removes_stray_files_from_the_cache(remote_and_cache):
    # Arrange
    _remote, cache = remote_and_cache
    _cache.ensure_cache()
    (cache / "templates" / "stray.txt").write_text("left behind")
    # Act
    _cache.ensure_cache()
    # Assert
    assert not (cache / "templates" / "stray.txt").exists()


def test_unreachable_remote_raises_cache_refresh_error(stale_cache):
    # Arrange
    # Act
    error = _raised(_cache.ensure_cache)
    # Assert
    assert isinstance(error, _cache.CacheRefreshError)


def test_refresh_error_names_cached_commit_age_and_opt_in(stale_cache):
    # Arrange
    cached = _git(stale_cache, "rev-parse", "--short", "HEAD")
    # Act
    message = str(_raised(_cache.ensure_cache))
    # Assert
    assert (cached in message, "days old" in message, "--offline" in message) == (
        True,
        True,
        True,
    )


def test_missing_branch_raises_cache_refresh_error(remote_and_cache):
    # Arrange
    _cache.ensure_cache()
    # Act
    error = _raised(lambda: _cache.ensure_cache(branch="no-such-branch"))
    # Assert
    assert isinstance(error, _cache.CacheRefreshError)


def test_clone_from_cache_copies_nothing_when_refresh_fails(stale_cache, tmp_path):
    # Arrange
    target = tmp_path / "project"
    # Act
    error = _raised(lambda: _cache.clone_template_from_cache("research", target))
    # Assert
    assert (isinstance(error, _cache.CacheRefreshError), target.exists()) == (
        True,
        False,
    )


def test_offline_serves_cache_and_warns_with_its_commit(stale_cache):
    # Arrange
    cached = _git(stale_cache, "rev-parse", "--short", "HEAD")
    # Act
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        root = _cache.ensure_cache(offline=True)
    # Assert
    assert (root, any(cached in str(w.message) for w in caught)) == (
        stale_cache,
        True,
    )


def test_offline_without_cache_raises(remote_and_cache):
    # Arrange
    # Act
    error = _raised(lambda: _cache.ensure_cache(offline=True))
    # Assert
    assert "no scitex-template cache" in str(error)


def test_offline_with_force_refresh_is_rejected(remote_and_cache):
    # Arrange
    # Act
    error = _raised(lambda: _cache.ensure_cache(offline=True, force_refresh=True))
    # Assert
    assert isinstance(error, ValueError)


def test_cli_clone_exits_nonzero_with_message_when_refresh_fails(stale_cache, tmp_path):
    # Arrange
    from click.testing import CliRunner

    from scitex_template.cli import main

    # Act
    result = CliRunner().invoke(main, ["clone", "research", str(tmp_path / "p")])
    # Assert
    assert (result.exit_code, "could not refresh" in result.output) == (3, True)
