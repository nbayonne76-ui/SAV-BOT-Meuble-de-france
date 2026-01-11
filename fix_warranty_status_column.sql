-- Fix warranty_status column size from VARCHAR(50) to VARCHAR(200)
-- Run this on Railway PostgreSQL database

BEGIN;

-- Increase warranty_status column size
ALTER TABLE sav_tickets
ALTER COLUMN warranty_status TYPE VARCHAR(200);

COMMIT;

-- Verify the change
SELECT
    column_name,
    data_type,
    character_maximum_length
FROM information_schema.columns
WHERE table_name = 'sav_tickets'
  AND column_name = 'warranty_status';
