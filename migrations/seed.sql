-- PostgreSQL database seed file
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS user_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    discord_id BIGINT NOT NULL,
    datacenter VARCHAR(32) NOT NULL,

    UNIQUE (discord_id)
)
