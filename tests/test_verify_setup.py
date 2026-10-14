"""Verify that setup evidence never prints any part of an API key."""
import contextlib
import importlib.util
import io
import os
from pathlib import Path
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "04-lab/mcp-client/verify_setup.py"
spec = importlib.util.spec_from_file_location("verify_setup", SCRIPT)
setup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(setup)


class SetupPrivacyTest(unittest.TestCase):
    def test_environment_output_does_not_disclose_key_prefix(self):
        key = "private-test-key-do-not-print"
        output = io.StringIO()
        with patch.dict(os.environ, {"GOOGLE_API_KEY": key}), \
                patch.object(Path, "exists", return_value=True), \
                patch("dotenv.load_dotenv"), contextlib.redirect_stdout(output):
            self.assertTrue(setup.check_environment())
        self.assertNotIn(key[:10], output.getvalue())
        self.assertIn("configured", output.getvalue())


if __name__ == "__main__":
    unittest.main()
