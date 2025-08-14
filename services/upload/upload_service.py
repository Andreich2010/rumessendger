import os
import json
import uuid
import datetime
import hashlib
import hmac
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer


def _sign(key: bytes, msg: str) -> bytes:
    return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()


def _signature_key(secret_key: str, date_stamp: str, region: str, service: str) -> bytes:
    k_date = _sign(('AWS4' + secret_key).encode('utf-8'), date_stamp)
    k_region = _sign(k_date, region)
    k_service = _sign(k_region, service)
    return _sign(k_service, 'aws4_request')


def presign_url(method: str, object_key: str, expires: int = 3600) -> str:
    access_key = os.environ['S3_ACCESS_KEY']
    secret_key = os.environ['S3_SECRET_KEY']
    region = os.environ.get('S3_REGION', 'us-east-1')
    endpoint = os.environ['S3_ENDPOINT'].rstrip('/')
    bucket = os.environ['S3_BUCKET']

    parsed = urllib.parse.urlparse(endpoint)
    host = parsed.netloc
    canonical_uri = f"/{bucket}/{urllib.parse.quote(object_key)}"

    algorithm = 'AWS4-HMAC-SHA256'
    now = datetime.datetime.utcnow()
    amz_date = now.strftime('%Y%m%dT%H%M%SZ')
    date_stamp = now.strftime('%Y%m%d')
    credential_scope = f"{date_stamp}/{region}/s3/aws4_request"
    credential = f"{access_key}/{credential_scope}"

    params = {
        'X-Amz-Algorithm': algorithm,
        'X-Amz-Credential': urllib.parse.quote(credential, safe=''),
        'X-Amz-Date': amz_date,
        'X-Amz-Expires': str(expires),
        'X-Amz-SignedHeaders': 'host',
    }
    canonical_query = '&'.join(f"{k}={v}" for k, v in sorted(params.items()))

    canonical_headers = f"host:{host}\n"
    signed_headers = 'host'
    payload_hash = 'UNSIGNED-PAYLOAD'
    canonical_request = '\n'.join([method, canonical_uri, canonical_query,
                                   canonical_headers, signed_headers, payload_hash])

    string_to_sign = '\n'.join([
        algorithm,
        amz_date,
        credential_scope,
        hashlib.sha256(canonical_request.encode('utf-8')).hexdigest(),
    ])

    signing_key = _signature_key(secret_key, date_stamp, region, 's3')
    signature = hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()

    canonical_query += f"&X-Amz-Signature={signature}"
    return f"{endpoint}{canonical_uri}?{canonical_query}"


class UploadHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != '/slot':
            self.send_response(404)
            self.end_headers()
            return

        length = int(self.headers.get('Content-Length', '0'))
        body = self.rfile.read(length)
        try:
            data = json.loads(body)
            filename = data['filename']
        except Exception:  # noqa: BLE001
            self.send_response(400)
            self.end_headers()
            return

        object_key = f"{uuid.uuid4()}_{filename}"
        put_url = presign_url('PUT', object_key)
        get_url = presign_url('GET', object_key)

        resp = json.dumps({'put': put_url, 'get': get_url, 'key': object_key})
        resp_bytes = resp.encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(resp_bytes)))
        self.end_headers()
        self.wfile.write(resp_bytes)


def make_server(port: int | None = None) -> HTTPServer:
    address = ('', port or int(os.environ.get('PORT', 8000)))
    return HTTPServer(address, UploadHandler)


if __name__ == '__main__':
    httpd = make_server()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:  # pragma: no cover
        pass
    finally:
        httpd.server_close()
