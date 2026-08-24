from pathlib import Path
import tempfile
import unittest

from voltcast.profiles import StepPoint, StepPowerProfile


class StepPowerProfileTests(unittest.TestCase):
    def test_zero_order_hold(self):
        profile = StepPowerProfile(
            [StepPoint(0, 0.2), StepPoint(10, 1.5), StepPoint(20, 0.4)]
        )
        self.assertEqual(profile.power_at(0), 0.2)
        self.assertEqual(profile.power_at(9.999), 0.2)
        self.assertEqual(profile.power_at(10), 1.5)
        self.assertEqual(profile.power_at(100), 0.4)

    def test_requires_zero_origin_and_increasing_times(self):
        with self.assertRaises(ValueError):
            StepPowerProfile([StepPoint(1, 1)])
        with self.assertRaises(ValueError):
            StepPowerProfile([StepPoint(0, 1), StepPoint(0, 2)])

    def test_csv_schema_is_explicit(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "profile.csv"
            source.write_text("time_s,power_w\n0,1.2\n60,2.4\n", encoding="utf-8")
            profile = StepPowerProfile.from_csv(source)
            self.assertEqual(profile.name, "profile")
            self.assertEqual(profile.power_at(61), 2.4)


if __name__ == "__main__":
    unittest.main()
