import configs


class DatabaseConfig:
    """Configuration for database connection."""

    HOST = configs.PG_HOST
    PORT = configs.PG_PORT
    USER = configs.PG_USER
    PASSWORD = configs.PG_PWD
    DATABASE = configs.PG_DB

    @property
    def dsn(self):
        """Constructs and returns the DSN string."""
        return f"dbname={self.DATABASE} user={self.USER} password={self.PASSWORD} host={self.HOST} port={self.PORT}"
