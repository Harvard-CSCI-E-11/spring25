DROP TABLE IF EXISTS api_keys;
DROP TABLE IF EXISTS post;

CREATE TABLE api_keys (
       api_key_id INTEGER PRIMARY KEY AUTOINCREMENT,
       api_key text(255) UNIQUE NOT NULL,
       api_secret_key_hash text(255) NOT NULL,
       created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
       last_used TIMESTAMP,
       remaining INTEGER DEFAULT 1000
);

CREATE UNIQUE INDEX api_key_index ON api_keys(api_key);

CREATE TABLE images (
       image_id INTEGER PRIMARY KEY AUTOINCREMENT,
       urn text(1023) UNIQUE NOT NULL,
       created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
       created_by INTEGER NOT NULL,
       annotations text(65535),
       FOREIGN KEY(created_by)
       REFERENCES api_keys(api_key_id)
         ON UPDATE RESTRICT
         ON DELETE RESTRICT
);

CREATE UNIQUE INDEX urn_index ON images(urn);
