import os
import json
import threading
import unittest
import urllib.request
import sys
from pathlib import Path

# Set env vars before importing the service
os.environ['ENV'] = 'DEV'
os.environ['FCM_SERVER_KEY_DEV'] = 'test-key'
os.environ['HMS_APP_ID'] = 'app'
os.environ['HMS_CLIENT_ID_DEV'] = 'client'
os.environ['HMS_CLIENT_SECRET_DEV'] = 'secret'

sys.path.append(str(Path(__file__).resolve().parent))
import push_gateway  # noqa: E402


class PushGatewayTest(unittest.TestCase):
    def _start(self):
        httpd = push_gateway.make_server(port=0)
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        return httpd, httpd.server_address[1]

    def _register(self, port: int, platform: str, token: str) -> None:
        data = json.dumps({
            'token': token,
            'jid': 'u@d',
            'resource': 'r',
            'platform': platform,
        }).encode('utf-8')
        req = urllib.request.Request(
            f'http://localhost:{port}/register',
            data=data,
            headers={'Content-Type': 'application/json'},
            method='POST',
        )
        urllib.request.urlopen(req).close()

    def test_health(self):
        httpd, port = self._start()
        with urllib.request.urlopen(f'http://localhost:{port}/health') as resp:
            self.assertEqual(resp.status, 200)
            self.assertEqual(resp.read(), b'ok')
        httpd.shutdown()
        httpd.server_close()

    def test_push_fcm(self):
        called: dict[str, tuple[str, str, str]] = {}

        def fake_send(token: str, title: str, body: str) -> None:
            called['args'] = (token, title, body)

        push_gateway.send_fcm = fake_send
        httpd, port = self._start()
        self._register(port, 'fcm', 'abc')
        data = json.dumps({
            'token': 'abc',
            'title': 'Hi',
            'body': 'Message',
        }).encode('utf-8')
        req = urllib.request.Request(
            f'http://localhost:{port}/push',
            data=data,
            headers={'Content-Type': 'application/json'},
            method='POST',
        )
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 202)
        self.assertEqual(called['args'], ('abc', 'Hi', 'Message'))
        httpd.shutdown()
        httpd.server_close()

    def test_push_hms(self):
        called: dict[str, tuple[str, str, str]] = {}

        def fake_send(token: str, title: str, body: str) -> None:
            called['args'] = (token, title, body)

        push_gateway.send_hms = fake_send
        httpd, port = self._start()
        self._register(port, 'hms', 'xyz')
        data = json.dumps({
            'token': 'xyz',
            'title': 'Hi',
            'body': 'Message',
        }).encode('utf-8')
        req = urllib.request.Request(
            f'http://localhost:{port}/push',
            data=data,
            headers={'Content-Type': 'application/json'},
            method='POST',
        )
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 202)
        self.assertEqual(called['args'], ('xyz', 'Hi', 'Message'))
        httpd.shutdown()
        httpd.server_close()


if __name__ == '__main__':
    unittest.main()
