import unittest

from core.update_checker import UpdateCheckError, _latest_release, compare_versions


class CompareVersionsTests(unittest.TestCase):
    def test_newer_version(self):
        self.assertEqual(compare_versions("v0.2.0", "0.1.0"), 1)

    def test_same_version_with_optional_v_prefix(self):
        self.assertEqual(compare_versions("v1.2.3", "1.2.3"), 0)

    def test_stable_version_is_newer_than_prerelease(self):
        self.assertEqual(compare_versions("0.1.0", "0.1.0-beta"), 1)

    def test_prerelease_is_older_than_stable_version(self):
        self.assertEqual(compare_versions("2.0.0-rc.1", "2.0.0"), -1)

    def test_numeric_prerelease_identifiers_compare_numerically(self):
        self.assertEqual(compare_versions("1.0.0-beta.10", "1.0.0-beta.2"), 1)

    def test_invalid_version_raises_value_error(self):
        with self.assertRaises(ValueError):
            compare_versions("latest", "1.0.0")

    def test_build_metadata_does_not_affect_precedence(self):
        self.assertEqual(compare_versions("1.2.3+build.2", "1.2.3+build.1"), 0)


class LatestReleaseTests(unittest.TestCase):
    def test_selects_highest_version_and_includes_prereleases(self):
        releases = [
            {"tag_name": "v0.2.0-beta.2", "draft": False},
            {"tag_name": "v0.1.0", "draft": False},
            {"tag_name": "v0.2.0-beta.1", "draft": False},
        ]
        self.assertEqual(_latest_release(releases)["tag_name"], "v0.2.0-beta.2")

    def test_ignores_drafts_and_unrecognized_tags(self):
        releases = [
            {"tag_name": "v9.0.0", "draft": True},
            {"tag_name": "nightly", "draft": False},
            {"tag_name": "v1.0.0", "draft": False},
        ]
        self.assertEqual(_latest_release(releases)["tag_name"], "v1.0.0")

    def test_no_valid_release_raises_update_error(self):
        with self.assertRaises(UpdateCheckError):
            _latest_release([])


if __name__ == "__main__":
    unittest.main()
