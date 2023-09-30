run:
	poetry run uvicorn app.main:app --reload

Run tests:
	docker exec -it ferry pytest -v -s

Coverage:
	docker exec -it ferry coverage run -m pytest
	docker exec -it ferry coverage report -m

migrations_create:
	docker exec -it ferry alembic revision --autogenerate -m $(comment)

migrations_run:
	docker exec -it ferry alembic upgrade head

migrations_downgrade:
	docker exec -it ferry alembic downgrade head

redis:
	docker exec -it ferry-redis redis-cli

database:
	docker exec -it ferry-db bash -c "su postgres -c 'psql'"


seed:
	docker exec -it cards python3 seed.py