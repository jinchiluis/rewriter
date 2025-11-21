from typing import Dict
import streamlit as st
from supabase import create_client, Client


class SupabaseLogger:
    """Simple and safe logger that won't crash if Supabase fails."""

    def __init__(self):
        try:
            url: str = st.secrets["SUPABASE_URL"]
            key: str = st.secrets["SUPABASE_KEY"]
            self.client: Client = create_client(url, key)
        except Exception as e:
            st.warning(f"⚠️ Could not connect to Supabase: {e}")
            self.client = None

    def log(self, data: Dict):
        """Insert a log record into the 'rewriter_logger' table (safe)."""
        if not self.client:
            return  # just skip if client not available

        try:
            self.client.table("rewriter_logger").insert(data).execute()
        except Exception:
            # silently ignore to prevent crashing
            pass

