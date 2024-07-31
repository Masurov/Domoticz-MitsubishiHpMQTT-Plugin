import unittest
from DomoticzVersion import DomoticzVersion


class TestVersion(unittest.TestCase):

    def test_version_creation_success(self):
        # Test successful creation of non-beta version
        success, version = DomoticzVersion.try_parse("2022.1")
        self.assertTrue(success)
        self.assertIsNotNone(version)
        self.assertEqual(version.year, 2022)
        self.assertEqual(version.minor, 1)
        self.assertFalse(version.is_beta)

        # Test successful creation of beta version
        success, version = DomoticzVersion.try_parse("2024.1 Beta")
        self.assertTrue(success)
        self.assertIsNotNone(version)
        self.assertEqual(version.year, 2024)
        self.assertEqual(version.minor, 1)
        self.assertTrue(version.is_beta)

    def test_version_creation_failure(self):
        # Test failure cases for invalid version strings
        success, version = DomoticzVersion.try_parse("invalid.version")
        self.assertFalse(success)
        self.assertIsNone(version)

        success, version = DomoticzVersion.try_parse("2023.1 Alpha")
        self.assertFalse(success)
        self.assertIsNone(version)

        success, version = DomoticzVersion.try_parse("2024")
        self.assertFalse(success)
        self.assertIsNone(version)

    def test_version_equality(self):
        success, v1 = DomoticzVersion.try_parse("2023.2")
        success, v2 = DomoticzVersion.try_parse("2023.2")
        success, v3 = DomoticzVersion.try_parse("2023.2 Beta")
        self.assertEqual(v1, v2)
        self.assertNotEqual(v1, v3)
        self.assertNotEqual(v2, v3)

    def test_version_inequality(self):
        success, v1 = DomoticzVersion.try_parse("2023.2")
        success, v2 = DomoticzVersion.try_parse("2023.2")
        success, v3 = DomoticzVersion.try_parse("2023.2 Beta")
        self.assertFalse(v1 != v2)
        self.assertTrue(v2 != v3)

    def test_version_strict_comparison(self):
        success, v2022_1 = DomoticzVersion.try_parse("2022.1")
        success, v2023_1 = DomoticzVersion.try_parse("2023.1")
        success, v2023_2 = DomoticzVersion.try_parse("2023.2")
        success, v2023_2_beta = DomoticzVersion.try_parse("2023.2 Beta")

        self.assertTrue(v2022_1 < v2023_1)
        self.assertTrue(v2023_1 < v2023_2)
        self.assertTrue(v2023_2 > v2023_2_beta)
        self.assertTrue(v2023_2_beta < v2023_2)
        self.assertTrue(v2023_2_beta > v2023_1)

    def test_version_comparison(self):
        success, v2022_1 = DomoticzVersion.try_parse("2022.1")
        success, v2023_1 = DomoticzVersion.try_parse("2023.1")
        success, v2023_2 = DomoticzVersion.try_parse("2023.2")
        success, v2023_2_beta = DomoticzVersion.try_parse("2023.2 Beta")

        self.assertTrue(v2022_1 <= v2022_1)
        self.assertTrue(v2022_1 <= v2023_1)
        self.assertTrue(v2023_1 <= v2023_2)
        self.assertTrue(v2023_2 >= v2023_2_beta)
        self.assertTrue(v2023_2_beta <= v2023_2)
        self.assertTrue(v2023_2_beta >= v2023_1)

    def test_beta_handling_true(self):
        success, version = DomoticzVersion.try_parse("2023.1 Beta")
        self.assertTrue(version.is_beta)

    def test_beta_handling_false(self):
        success, version = DomoticzVersion.try_parse("2023.1")
        self.assertFalse(version.is_beta)

    def test_version_string_representation(self):
        success, v1 = DomoticzVersion.try_parse("2022.1")
        success, v2 = DomoticzVersion.try_parse("2023.2 Beta")
        self.assertEqual(str(v1), "2022.1")
        self.assertEqual(str(v2), "2023.2 Beta")


if __name__ == '__main__':
    unittest.main()
