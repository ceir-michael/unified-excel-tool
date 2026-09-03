import json
import re
import urllib.error
import urllib.request
from dataclasses import dataclass

from constants import APP_NAME, APP_REPOSITORY, APP_VERSION


GITHUB_API_URL = f"https://api.github.com/repos/{APP_REPOSITORY}/releases?per_page=30"
_VERSION_PATTERN = re.compile(
    r"^v?(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)"
    r"(?:[-.]?(?P<prerelease>[0-9A-Za-z.-]+))?"
    r"(?:\+[0-9A-Za-z.-]+)?$"
)


class UpdateCheckError(RuntimeError):
    """Raised when update information cannot be retrieved or understood."""


@dataclass(frozen=True)
class UpdateInfo:
    current_version: str
    latest_version: str
    release_url: str
    release_name: str

    @property
    def update_available(self) -> bool:
        return compare_versions(self.latest_version, self.current_version) > 0


def _version_key(version: str) -> tuple:
    match = _VERSION_PATTERN.fullmatch(version.strip())
    if not match:
        raise ValueError(f"Unsupported version format: {version}")

    prerelease = match.group("prerelease")
    prerelease_key = ()
    if prerelease:
        prerelease_key = tuple(
            (0, int(part)) if part.isdigit() else (1, part.lower())
            for part in prerelease.split(".")
        )

    return (
        int(match.group("major")),
        int(match.group("minor")),
        int(match.group("patch")),
        1 if prerelease is None else 0,
        prerelease_key,
    )


def compare_versions(left: str, right: str) -> int:
    """Return 1, 0, or -1 when left is newer, equal, or older."""
    left_key = _version_key(left)
    right_key = _version_key(right)
    return (left_key > right_key) - (left_key < right_key)


def _latest_release(releases: list) -> dict:
    candidates = []
    for release in releases:
        if not isinstance(release, dict) or release.get("draft"):
            continue

        version = str(release.get("tag_name", "")).strip()
        try:
            key = _version_key(version)
        except ValueError:
            continue
        candidates.append((key, release))

    if not candidates:
        raise UpdateCheckError("No published releases are available yet.")
    return max(candidates, key=lambda candidate: candidate[0])[1]


def check_for_updates(timeout: float = 10) -> UpdateInfo:
    request = urllib.request.Request(
        GITHUB_API_URL,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": f"{APP_NAME.replace(' ', '-')}/{APP_VERSION}",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            raise UpdateCheckError("No published releases are available yet.") from exc
        raise UpdateCheckError(f"GitHub returned an error (HTTP {exc.code}).") from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise UpdateCheckError(
            "Could not connect to GitHub. Check your internet connection and try again."
        ) from exc
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise UpdateCheckError("GitHub returned an invalid update response.") from exc

    if not isinstance(payload, list):
        raise UpdateCheckError("GitHub returned an invalid update response.")

    latest_release = _latest_release(payload)
    latest_version = str(latest_release.get("tag_name", "")).strip()
    release_url = str(latest_release.get("html_url", "")).strip()
    release_name = str(latest_release.get("name") or latest_version).strip()

    if not latest_version or not release_url:
        raise UpdateCheckError("The latest release is missing version information.")

    try:
        compare_versions(latest_version, APP_VERSION)
    except ValueError as exc:
        raise UpdateCheckError(str(exc)) from exc

    return UpdateInfo(
        current_version=APP_VERSION,
        latest_version=latest_version,
        release_url=release_url,
        release_name=release_name,
    )
