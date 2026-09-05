-- =====================================================================
-- Pexo — Additive migration: refresh_token table
-- Not part of the original schema.sql. Run this once against the same
-- Neon database schema.sql was applied to, before login/refresh will work.
-- Safe to re-run: guarded with IF NOT EXISTS.
-- =====================================================================

CREATE TABLE IF NOT EXISTS refresh_token (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id           UUID NOT NULL REFERENCES app_user(id) ON DELETE CASCADE,
  token_hash        VARCHAR(255) NOT NULL UNIQUE,
  expires_at        TIMESTAMPTZ NOT NULL,
  revoked_at        TIMESTAMPTZ,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_refresh_token_user ON refresh_token(user_id);
