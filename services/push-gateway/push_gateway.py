import os
import json
import time
import urllib.request
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

ENV = os.environ.get('ENV', 'DEV').upper()
RATE_LIMIT = float(os.environ.get('PUSH_RATE_LIMIT_SECONDS', '1'))
REGISTRATIONS: dict[str, dict[str, str]] = {}
LAST_PUSH: dict[str, float] = {}


def _env_var(name: str) -> str:
    return os.environ.get(f'{name}_{ENV}', os.environ.get(name, ''))


def send_fcm(token: str, title: str, body: str) -> None:
    server_key = _env_var('FCM_SERVER_KEY')
    message = {
        'to': token,
        'notification': {'title': title, 'body': body},
    }
    req = urllib.request.Request(
        'https://fcm.googleapis.com/fcm/send',
        data=json.dumps(message).encode('utf-8'),
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'key={server_key}',
        },
    )
    with urllib.request.urlopen(req) as resp:  # noqa: S310
        resp.read()


def _hms_access_token() -> str:
    data = urllib.parse.urlencode({
        'grant_type': 'client_credentials',
        'client_id': _env_var('HMS_CLIENT_ID'),
        'client_secret': _env_var('HMS_CLIENT_SECRET'),
    }).encode('utf-8')
    req = urllib.request.Request(
        'https://oauth-login.cloud.huawei.com/oauth2/v3/token',
        data=data,
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
    )
    with urllib.request.urlopen(req) as resp:  # noqa: S310
        payload = json.loads(resp.read().decode('utf-8'))
        return payload['access_token']


def send_hms(token: str, title: str, body: str) -> None:
    app_id = _env_var('HMS_APP_ID') or os.environ['HMS_APP_ID']
    access_token = _hms_access_token()
    url = f'https://push-api.cloud.huawei.com/v1/{app_id}/messages:send'
    message = {
        'validate_only': False,
        'message': {
            'token': [token],
            'notification': {'title': title, 'body': body},
        },
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(message).encode('utf-8'),
        headers={
            'Content-Type': 'application/json;charset=utf-8',
            'Authorization': f'Bearer {access_token}',
        },
    )
    with urllib.request.urlopen(req) as resp:  # noqa: S310
        resp.read()


class PushGatewayHandler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'ok')
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):  # noqa: N802
        length = int(self.headers.get('Content-Length', '0'))
        body = self.rfile.read(length)
        if self.path == '/register':
            try:
                data = json.loads(body)
                token = data['token']
                REGISTRATIONS[token] = {
                    'jid': data['jid'],
                    'resource': data['resource'],
                    'platform': data['platform'],
                }
            except Exception:  # noqa: BLE001
                self.send_response(400)
                self.end_headers()
                return
            self.send_response(200)
            self.end_headers()
            return

        if self.path != '/push':
            self.send_response(404)
            self.end_headers()
            return
        try:
            data = json.loads(body)
            token = data['token']
            title = data.get('title', '')
            message = data.get('body', '')
        except Exception:  # noqa: BLE001
            self.send_response(400)
            self.end_headers()
            return
        reg = REGISTRATIONS.get(token)
        if not reg:
            self.send_response(404)
            self.end_headers()
            return
        now = time.time()
        last = LAST_PUSH.get(token, 0)
        if now - last < RATE_LIMIT:
            self.send_response(429)
            self.end_headers()
            return
        LAST_PUSH[token] = now
        platform = reg['platform']
        try:
            for attempt in range(3):
                try:
                    if platform == 'fcm':
                        send_fcm(token, title, message)
                    elif platform == 'hms':
                        send_hms(token, title, message)
                    else:
                        raise ValueError('unknown platform')
                    break
                except Exception:  # noqa: BLE001
                    if attempt == 2:
                        raise
                    time.sleep(2 ** attempt)
        except Exception:  # noqa: BLE001
            self.send_response(500)
            self.end_headers()
            return

        self.send_response(202)
        self.end_headers()


def make_server(port: int | None = None) -> HTTPServer:
    address = ('', port or int(os.environ.get('PORT', 8000)))
    return HTTPServer(address, PushGatewayHandler)


if __name__ == '__main__':
    httpd = make_server()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:  # pragma: no cover
        pass
    finally:
        httpd.server_close()
