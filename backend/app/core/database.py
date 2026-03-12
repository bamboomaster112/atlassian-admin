"""Supabase client for database operations."""

from supabase import create_client, Client
from .config import settings

_client: Client | None = None


def get_supabase() -> Client:
    """Return a singleton Supabase client using the service-role key."""
    global _client
    if _client is None:
        _client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_ROLE_KEY,
        )
    return _client


async def init_db():
    """Verify Supabase connectivity on startup."""
    try:
        sb = get_supabase()
        sb.table("sync_history").select("id").limit(1).execute()
    except Exception as e:
        print(f"[WARNING] Supabase connectivity check failed: {e}")
        print("Make sure tables are created — see supabase/migrations/001_create_tables.sql")
