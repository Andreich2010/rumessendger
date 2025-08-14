# Push Gateway

This service receives push notifications from ejabberd and forwards them to
mobile push providers like Firebase Cloud Messaging (FCM) and Huawei Mobile
Services (HMS).

## Environment variables

- `PORT` – HTTP port to listen on (default `8000`).
- `FCM_SERVER_KEY` – server key for Firebase Cloud Messaging.
- `HMS_APP_ID` – Huawei application ID.
- `HMS_CLIENT_ID` – Huawei client ID.
- `HMS_CLIENT_SECRET` – Huawei client secret.

## API

### `GET /health`

Returns `200 OK` with body `ok`.

### `POST /push`

Request body:

```json
{
  "platform": "fcm",   // or "hms"
  "token": "device-token",
  "title": "Hello",
  "body": "World"
}
```

The service forwards the notification to the selected provider.
On success a `202 Accepted` response is returned.

## ejabberd integration

Configure ejabberd to delegate push notifications to this gateway:

```yaml
modules:
  mod_push:
    service_url: http://push-gateway:8000/push
```

Ejabberd will POST the notification payload and the gateway will relay it to
the appropriate mobile push service.
