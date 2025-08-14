import os
import json
import threading
import unittest
import urllib.request
import sys
from pathlib import Path

# Environment variables must be set before importing the service
os.environ['S3_ACCESS_KEY'] = 'test'
os.environ['S3_SECRET_KEY'] = 'secret'
os.environ['S3_REGION'] = 'us-east-1'
os.environ['S3_ENDPOINT'] = 'http://localhost:9000'
os.environ['S3_BUCKET'] = 'bucket'
os.environ['MAX_UPLOAD_SIZE'] = '1024'
os.environ['ALLOWED_TYPES'] = 'text/plain'
os.environ['UPLOAD_TTL'] = '600'
os.environ['CORS_ALLOW_ORIGIN'] = '*'

sys.path.append(str(Path(__file__).resolve().parent))
import upload_service  # noqa: E402


class UploadServiceTest(unittest.TestCase):
    def test_slot_endpoint(self):
        httpd = upload_service.make_server(port=0)
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        port = httpd.server_address[1]

        data = json.dumps({
            'filename': 'hello.txt',
            'size': 10,
            'content_type': 'text/plain',
        }).encode('utf-8')
        req = urllib.request.Request(
            f'http://localhost:{port}/slot',
            data=data,
            headers={'Content-Type': 'application/json'},
            method='POST',
        )
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)
            payload = json.loads(resp.read().decode('utf-8'))
            self.assertIn('put', payload)
            self.assertIn('get', payload)

        httpd.shutdown()
        httpd.server_close()


if __name__ == '__main__':
    unittest.main()
