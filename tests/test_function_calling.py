"""Exercise the real Gemini SDK against a transient HTTP failure."""
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

import httpx
from google import genai
from google.genai import types


class FunctionCallingRetryTest(unittest.TestCase):
    def test_recovers_from_temporary_service_unavailable(self):
        requests = []

        def respond(request):
            requests.append(request)
            if len(requests) == 1:
                return httpx.Response(503, json={"error": {"code": 503, "message": "Temporary overload", "status": "UNAVAILABLE"}})
            return httpx.Response(200, json={"candidates": [{"content": {"role": "model", "parts": [{"text": "Recovered"}]}, "finishReason": "STOP"}]})

        real_client = genai.Client
        transport_client = httpx.Client(transport=httpx.MockTransport(respond))

        def create_client(**kwargs):
            supplied = kwargs.get("http_options")
            retry = supplied.retry_options if supplied else None
            if retry:
                retry.initial_delay = retry.max_delay = retry.jitter = 0.001
            return real_client(api_key="fake-test-key", http_options=types.HttpOptions(httpx_client=transport_client, retry_options=retry))

        source = Path(__file__).resolve().parents[1] / "01-function-calling/weather_function_calling.py"
        spec = importlib.util.spec_from_file_location("weather_function_calling", source)
        weather = importlib.util.module_from_spec(spec)
        with patch("google.genai.Client", side_effect=create_client):
            spec.loader.exec_module(weather)
        try:
            self.assertEqual(weather.run("Hello"), "Recovered")
            self.assertEqual(len(requests), 2)
        finally:
            weather.client.close()


if __name__ == "__main__":
    unittest.main()
