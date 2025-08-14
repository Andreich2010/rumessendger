# Upload Service

This service provides pre-signed S3 URLs for direct file uploads. It is intended
for ejabberd's [HTTP File Upload](https://xmpp.org/extensions/xep-0363.html)
module.

## Environment variables

- `PORT` – HTTP port to listen on (default `8000`).
- `S3_ENDPOINT` – MinIO/S3 endpoint, e.g. `http://minio:9000`.
- `S3_REGION` – AWS region (default `us-east-1`).
- `S3_ACCESS_KEY` – S3 access key.
- `S3_SECRET_KEY` – S3 secret key.
- `S3_BUCKET` – bucket name where uploads will be stored.

## API

`POST /slot`

Request body:

```json
{ "filename": "example.png" }
```

Response body:

```json
{
  "put": "https://…",
  "get": "https://…",
  "key": "generated-object-key"
}
```

The `put` URL accepts a `PUT` request with the file data. The `get` URL is a
pre-signed link to download the uploaded file.

## ejabberd integration

Configure ejabberd to delegate slot requests to this service:

```yaml
modules:
  mod_http_upload:
    service_url: http://upload:8000/slot
    max_file_size: 10485760
```

Ejabberd will POST the file name to `/slot` and relay the returned URLs to the
client.
