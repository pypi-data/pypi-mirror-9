--
-- Load pgcrypto for UUID generation
--
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

--
-- Convert timestamps to milliseconds epoch integer
--
CREATE OR REPLACE FUNCTION as_epoch(ts TIMESTAMP) RETURNS BIGINT AS $$
BEGIN
    RETURN (EXTRACT(EPOCH FROM ts) * 1000)::BIGINT;
END;
$$ LANGUAGE plpgsql
IMMUTABLE;

--
-- Actual records
--
CREATE TABLE IF NOT EXISTS records (
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    user_id VARCHAR(256) NOT NULL,
    resource_name  VARCHAR(256) NOT NULL,

    -- Timestamp is relevant because adequate semantically.
    -- Since the HTTP API manipulates integers, it could make sense
    -- to replace the timestamp columns type by integer.
    last_modified TIMESTAMP NOT NULL,

    -- Consider using binary JSON (JSONB, postgresql 9.4+, 2x faster).
    data JSON NOT NULL DEFAULT '{}'
);

DROP INDEX IF EXISTS idx_records_user_id_resource_name_last_modified;
CREATE UNIQUE INDEX idx_records_user_id_resource_name_last_modified
    ON records(user_id, resource_name, last_modified DESC);
DROP INDEX IF EXISTS idx_records_user_id;
CREATE INDEX idx_records_user_id ON records(user_id);
DROP INDEX IF EXISTS idx_records_resource_name;
CREATE INDEX idx_records_resource_name ON records(resource_name);
DROP INDEX IF EXISTS idx_records_last_modified;
CREATE INDEX idx_records_last_modified ON records(last_modified);
DROP INDEX IF EXISTS idx_records_last_modified_epoch;
CREATE INDEX idx_records_last_modified_epoch ON records(as_epoch(last_modified));
DROP INDEX IF EXISTS idx_records_id;
CREATE INDEX idx_records_id ON records(id);


--
-- Deleted records, without data.
--
CREATE TABLE IF NOT EXISTS deleted (
    id UUID,
    user_id VARCHAR(256) NOT NULL,
    resource_name  VARCHAR(256) NOT NULL,
    last_modified TIMESTAMP NOT NULL
);
DROP INDEX IF EXISTS idx_records_user_id_resource_name_last_modified;
CREATE UNIQUE INDEX idx_records_user_id_resource_name_last_modified
    ON records(user_id, resource_name, last_modified DESC);
DROP INDEX IF EXISTS idx_deleted_id;
CREATE UNIQUE INDEX idx_deleted_id ON deleted(id);
DROP INDEX IF EXISTS idx_deleted_user_id;
CREATE INDEX idx_deleted_user_id ON deleted(user_id);
DROP INDEX IF EXISTS idx_deleted_resource_name;
CREATE INDEX idx_deleted_resource_name ON deleted(resource_name);
DROP INDEX IF EXISTS idx_deleted_last_modified;
CREATE INDEX idx_deleted_last_modified ON deleted(last_modified);
DROP INDEX IF EXISTS idx_deleted_last_modified_epoch;
CREATE INDEX idx_deleted_last_modified_epoch ON deleted(as_epoch(last_modified));

--
-- Helper that returns the current collection timestamp.
--
CREATE OR REPLACE FUNCTION resource_timestamp(uid VARCHAR, resource VARCHAR)
RETURNS TIMESTAMP AS $$
DECLARE
    ts_records TIMESTAMP;
    ts_deleted TIMESTAMP;
BEGIN
    --
    -- This is fast because an index was created for ``user_id``,
    -- ``resource_name``, and ``last_modified`` with descending sorting order.
    --
    SELECT last_modified INTO ts_records
      FROM records
     WHERE user_id = uid
       AND resource_name = resource
     ORDER BY last_modified DESC LIMIT 1;

    SELECT last_modified INTO ts_deleted
      FROM deleted
     WHERE user_id = uid
       AND resource_name = resource
     ORDER BY last_modified DESC LIMIT 1;

    -- Latest of records/deleted or current if empty
    RETURN coalesce(greatest(ts_deleted, ts_records), localtimestamp);
END;
$$ LANGUAGE plpgsql;

--
-- Triggers to set last_modified on INSERT/UPDATE
--
DROP TRIGGER IF EXISTS tgr_records_last_modified ON records;
DROP TRIGGER IF EXISTS tgr_deleted_last_modified ON deleted;

CREATE OR REPLACE FUNCTION bump_timestamp()
RETURNS trigger AS $$
DECLARE
    previous TIMESTAMP;
    current TIMESTAMP;
BEGIN
    --
    -- This bumps the current timestamp to 1 msec in the future if the previous
    -- timestamp is equal to the current one (or higher if was bumped already).
    --
    -- If a bunch of requests from the same user on the same collection
    -- arrive in the same millisecond, the unicity constraint can raise
    -- an error (operation is cancelled).
    -- See https://github.com/mozilla-services/cliquet/issues/25
    --
    previous := resource_timestamp(NEW.user_id, NEW.resource_name);
    current := localtimestamp;

    IF previous >= current THEN
        current := previous + INTERVAL '1 milliseconds';
    END IF;

    NEW.last_modified := current;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tgr_records_last_modified
BEFORE INSERT OR UPDATE ON records
FOR EACH ROW EXECUTE PROCEDURE bump_timestamp();

CREATE TRIGGER tgr_deleted_last_modified
BEFORE INSERT OR UPDATE ON deleted
FOR EACH ROW EXECUTE PROCEDURE bump_timestamp();

--
-- Metadata table
--
CREATE TABLE IF NOT EXISTS metadata (
    name VARCHAR(128) NOT NULL,
    value VARCHAR(512) NOT NULL
);
INSERT INTO metadata (name, value) VALUES ('created_at', NOW()::TEXT);


-- Set storage schema version.
-- Should match ``cliquet.storage.postgresql.PostgreSQL.schema_version``
INSERT INTO metadata (name, value) VALUES ('storage_schema_version', '3');
