#!/bin/sh
set -e

DATE=$(date +%Y%m%d)
BACKUP_DIR=${BACKUP_DIR:-/backups}
mkdir -p "$BACKUP_DIR"

pg_dump -h ${PGHOST:-postgres} -U ${POSTGRES_USER:-ejabberd} ${POSTGRES_DB:-ejabberd} > "$BACKUP_DIR/db_$DATE.sql"

mc ls --versions ${MINIO_ALIAS:-minio}/${MINIO_BUCKET:-uploads} > "$BACKUP_DIR/minio_versions_$DATE.txt"
