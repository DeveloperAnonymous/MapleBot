import postgresql.driver as pg
import configs

db = None

def conn():
    global db
    if db is None:
        db = pg.connect(
            host = configs.PG_HOST,
            port = configs.PG_PORT,
            user = configs.PG_USER,
            password = configs.PG_PWD
        )

    return db