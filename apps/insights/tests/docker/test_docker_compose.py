from testcontainers.postgres import PostgresContainer


def test_postgres_connection():
    with PostgresContainer("postgres:15-alpine") as postgres:
        engine = create_engine(postgres.get_connection_url())
        assert engine.connect()
