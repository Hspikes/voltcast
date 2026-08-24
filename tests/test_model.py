import unittest

from voltcast.model import BatteryParameters, open_circuit_voltage, operating_point, simulate
from voltcast.profiles import StepPowerProfile


class BatteryModelTests(unittest.TestCase):
    def setUp(self):
        self.battery = BatteryParameters()

    def test_ocv_is_monotonic_and_bounded(self):
        values = [open_circuit_voltage(index / 20, self.battery) for index in range(21)]
        self.assertEqual(values, sorted(values))
        self.assertAlmostEqual(values[0], self.battery.ocv_min_v)
        self.assertAlmostEqual(values[-1], self.battery.ocv_min_v + self.battery.ocv_span_v)

    def test_constant_power_solution_closes_power_balance(self):
        point = operating_point(4.0, 0.8, 0.03, 0.01, self.battery)
        self.assertIsNotNone(point)
        assert point is not None
        self.assertAlmostEqual(point.current_a * point.terminal_voltage_v, 4.0, places=9)

    def test_heavier_load_shortens_endurance(self):
        light = simulate(StepPowerProfile.constant(1.0, "light"), self.battery, step_s=10)
        heavy = simulate(StepPowerProfile.constant(7.0, "heavy"), self.battery, step_s=10)
        self.assertLess(heavy.time_to_empty_h, light.time_to_empty_h)

    def test_lower_initial_soc_shortens_endurance(self):
        profile = StepPowerProfile.constant(4.0)
        full = simulate(profile, self.battery, initial_soc=1.0, step_s=10)
        half = simulate(profile, self.battery, initial_soc=0.5, step_s=10)
        self.assertLess(half.time_to_empty_h, full.time_to_empty_h)

    def test_demo_aging_reduces_endurance(self):
        profile = StepPowerProfile.constant(4.0)
        new = simulate(profile, self.battery, step_s=10)
        aged = simulate(profile, self.battery.aged(), step_s=10)
        self.assertLess(aged.time_to_empty_h, new.time_to_empty_h)

    def test_infeasible_constant_power_is_reported(self):
        result = simulate(StepPowerProfile.constant(500.0), self.battery)
        self.assertEqual(result.stop_reason, "power-collapse")
        self.assertEqual(result.stop_time_s, 0)

    def test_trace_contains_physical_state(self):
        result = simulate(
            StepPowerProfile.constant(3.0),
            self.battery,
            max_time_s=600,
            step_s=5,
            sample_interval_s=60,
        )
        self.assertGreaterEqual(len(result.samples), 10)
        self.assertTrue(all(sample.current_a >= 0 for sample in result.samples))
        self.assertTrue(all(0 <= sample.soc <= 1 for sample in result.samples))


if __name__ == "__main__":
    unittest.main()
