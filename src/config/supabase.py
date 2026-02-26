"""Supabase client factory."""
from functools import lru_cache
from typing import Optional

from supabase import Client, create_client

from src.models.config import load_settings


@lru_cache
def get_supabase_client(use_service_role: bool = True) -> Client:
    """Get cached Supabase client."""
    settings = load_settings()
    key = settings.supabase_secret_key if use_service_role else settings.supabase_publishable_key
    return create_client(settings.supabase_url, key)
