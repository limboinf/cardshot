import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

import server as app_server


class PreviewEndpointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.previous_cards_dir = app_server.CARDS_DIR
        app_server.CARDS_DIR = Path(cls.temp_dir.name)
        (app_server.CARDS_DIR / "card.html").write_text(
            "<html><head></head><body style='width:1080px;height:1440px'>Card</body></html>",
            encoding="utf-8",
        )
        cls.httpd = ThreadingHTTPServer(("127.0.0.1", 0), app_server.Handler)
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.httpd.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        cls.thread.join()
        app_server.CARDS_DIR = cls.previous_cards_dir
        cls.temp_dir.cleanup()

    def test_returns_card_with_requested_adaptive_dimensions(self):
        with urllib.request.urlopen(
            self.base_url + "/api/preview?f=card.html&w=1920&h=1080"
        ) as response:
            body = response.read().decode("utf-8")

        self.assertEqual(response.status, 200)
        self.assertEqual(response.headers.get_content_type(), "text/html")
        self.assertIn("width: 1920px !important", body)
        self.assertIn("height: 1080px !important", body)
        self.assertIn('<base href="/cards/">', body)

    def test_rejects_invalid_dimensions(self):
        with self.assertRaises(urllib.error.HTTPError) as caught:
            urllib.request.urlopen(
                self.base_url + "/api/preview?f=card.html&w=0&h=1080"
            )

        self.assertEqual(caught.exception.code, 400)
        payload = json.loads(caught.exception.read().decode("utf-8"))
        self.assertIn("宽高", payload["error"])


if __name__ == "__main__":
    unittest.main()
