# rumessendger

## Purpose

Rumessendger provides a lightweight XMPP messaging stack for local development
and experimentation.  The project bundles **ejabberd** with a SQL database,
cache, object storage and auxiliary services so you can explore XMPP features
without assembling the infrastructure yourself.
=======
- **Upload Service** – provides pre-signed S3 URLs for HTTP file uploads.
  See [services/upload](services/upload/README.md).
- **Push Gateway** – accepts push notifications from ejabberd and forwards
  them to FCM or HMS.
  See [services/push-gateway](services/push-gateway/README.md).

## Architecture

The Docker Compose stack starts the following components:

- **ejabberd** – XMPP server that exposes client and server ports and hosts the
  core messaging logic.
- **PostgreSQL** – persistent storage for ejabberd modules such as message
  archive management.
- **Redis** – cache used by ejabberd for quick lookups and state.
- **MinIO** – S3-compatible storage backing the upload service.
- **Upload Service** – issues pre-signed S3 URLs for HTTP file uploads.
- **Push Gateway** – forwards XMPP push notifications to mobile push services.
- **Android Client** – example mobile client that consumes the stack.

## Supported XEPs

Ejabberd is configured with modules implementing several core XMPP Extension
Protocols (XEPs):

- [XEP-0198: Stream Management](https://xmpp.org/extensions/xep-0198.html)
- [XEP-0280: Message Carbons](https://xmpp.org/extensions/xep-0280.html)
- [XEP-0313: Message Archive Management](https://xmpp.org/extensions/xep-0313.html)
- [XEP-0357: Push Notifications](https://xmpp.org/extensions/xep-0357.html)
- [XEP-0363: HTTP File Upload](https://xmpp.org/extensions/xep-0363.html)

## Quick start

### Prerequisites

- [Docker](https://docs.docker.com/engine/install/)
- [Docker Compose](https://docs.docker.com/compose/install/)

Create a `certs/` directory and place `fullchain.pem` and `privkey.pem` inside
for TLS support.  Self-signed certificates are sufficient for development.

### Environment variables

The stack uses several environment variables which can be overridden with a
`.env` file or in your shell:

- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` – database credentials
  for ejabberd.
- `MINIO_ROOT_USER`, `MINIO_ROOT_PASSWORD` – credentials for the MinIO server.
- `ERLANG_NODE`, `EJABBERD_LOGLEVEL`, `EJABBERD_CERTFILE`, `EJABBERD_KEYFILE`
  – ejabberd runtime configuration.
- `PORT`, `S3_ENDPOINT`, `S3_REGION`, `S3_ACCESS_KEY`, `S3_SECRET_KEY`,
  `S3_BUCKET` – upload service configuration.

### Launching the stack

```bash
# start all containers in the background
docker-compose up -d
```

The services will be available on their default ports:

- ejabberd: 5222 (C2S), 5269 (S2S), 5280 (Web/HTTP upload)
- PostgreSQL: 5432
- Redis: 6379
- MinIO: 9000 (API) and 9001 (console)

## TLS certificates

The `docker-compose.yml` mounts a local `certs/` directory into the ejabberd
container. Place your TLS certificate and key in this directory as
`fullchain.pem` and `privkey.pem` respectively:

```bash
mkdir certs
# copy your certificate files into the certs/ directory
```

You can obtain certificates from Let's Encrypt using tools such as
[Certbot](https://certbot.eff.org/) or create self-signed certificates with
`openssl` for testing purposes.

After adding or renewing certificates, restart ejabberd:

```bash
docker-compose restart ejabberd
```

## Configuration

The ejabberd configuration is located at `ejabberd/ejabberd.yml`. Adjust this
file to enable additional modules or change database credentials as needed.

## Documentation

- [Ejabberd Modules](https://docs.ejabberd.im/admin/guide/configuration/#modules)
- [Upload Service](services/upload/README.md)
- [Push Gateway](https://github.com/rumessendger/push-gateway)
- [Android Client](https://github.com/rumessendger/android-client)

