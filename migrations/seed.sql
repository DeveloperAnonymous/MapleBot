-- PostgreSQL database seed file
CREATE TABLE IF NOT EXISTS user_settings (
    id BIGINT PRIMARY KEY,
    region VARCHAR(32) NOT NULL,
    datacenter VARCHAR(32) NOT NULL,
    world VARCHAR(32) NOT NULL
)
