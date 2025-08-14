.PHONY: up down logs psql backup

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

psql:
	docker compose exec postgres psql -U $${POSTGRES_USER:-ejabberd} $${POSTGRES_DB:-ejabberd}

backup:
	./scripts/backup.sh
