import contextlib
import io
import json
import os
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import patch

from notification import notification


class NotificationTests(unittest.TestCase):
    def test_caller_posts_json_and_survives_http_failure(self):
        received = []

        class Receiver(BaseHTTPRequestHandler):
            def do_POST(self):
                payload = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                received.append((self.headers["Content-Type"], payload))
                self.send_response(503 if self.path.endswith("fail") else 200)
                self.end_headers()
                self.wfile.write(b"do not log response body")

            def log_message(self, *args):
                pass

        with ThreadingHTTPServer(("127.0.0.1", 0), Receiver) as server:
            worker = threading.Thread(target=server.serve_forever, daemon=True)
            worker.start()
            try:
                for path in ("/hooks/test", "/hooks/fail"):
                    hook = "http://127.0.0.1:%s%s" % (server.server_port, path)
                    output = io.StringIO()
                    with patch.dict(os.environ, {"MATTERMOST_WEBHOOK_URL": hook}), contextlib.redirect_stdout(output):
                        notification('Trade Walls: test "quote"\nnext line')
                    self.assertNotIn(hook, output.getvalue())
                    self.assertNotIn("do not log response body", output.getvalue())
            finally:
                server.shutdown()
                worker.join()
        self.assertEqual(len(received), 2)
        self.assertTrue(all(c == "application/json" for c, _ in received))
        self.assertTrue(all(p == {"text": 'Trade Walls: test "quote"\nnext line'} for _, p in received))

    def test_missing_or_blank_setting_never_uses_retired_webhook(self):
        for value in ("", "   "):
            with patch.dict(os.environ, {"MATTERMOST_WEBHOOK_URL": value, "WEBHOOK_URL": "http://127.0.0.1:1/retired"}), patch("requests.post") as post, contextlib.redirect_stdout(io.StringIO()) as output:
                notification("local message")
            post.assert_not_called()
            self.assertIn("local message", output.getvalue())


if __name__ == "__main__":
    unittest.main()
