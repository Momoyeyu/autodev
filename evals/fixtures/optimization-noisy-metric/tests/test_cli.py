import unittest

from src.cli import initialize


class CliTest(unittest.TestCase):
    def test_registers_commands(self):
        self.assertEqual(initialize()["commands"], ["build", "test", "deploy"])


if __name__ == "__main__":
    unittest.main()
