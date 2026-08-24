from pathlib import Path
import tempfile
import unittest

from voltcast.cli import main


class CliTests(unittest.TestCase):
    def test_simulate_writes_trace(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            profile = root / "load.csv"
            output = root / "trace.csv"
            profile.write_text("time_s,power_w\n0,3.0\n", encoding="utf-8")
            status = main(
                [
                    "simulate",
                    str(profile),
                    "--max-hours",
                    "0.1",
                    "--output",
                    str(output),
                ]
            )
            self.assertEqual(status, 0)
            self.assertTrue(output.exists())
            self.assertIn("terminal_voltage_v", output.read_text(encoding="utf-8").splitlines()[0])


if __name__ == "__main__":
    unittest.main()
