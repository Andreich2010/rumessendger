# rumessendger

This repository contains a simple Docker Compose setup for the messaging stack
based on **ejabberd**, **PostgreSQL**, **Redis** and **MinIO**. It is intended for
local development and experimentation.

## Running the stack

1. Ensure Docker and Docker Compose are installed.
2. Start all services:

   ```bash
   docker-compose up -d
   ```
3. The services will be available on their default ports:
   - ejabberd: 5222 (C2S), 5269 (S2S), 5280 (Web/HTTP Upload)
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
