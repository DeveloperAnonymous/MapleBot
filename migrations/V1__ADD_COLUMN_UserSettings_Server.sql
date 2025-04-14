ALTER TABLE user_settings
    ADD COLUMN if not exists server VARCHAR(32) NULL;
