from typing import Dict
import streamlit as st
from supabase import create_client, Client


class SupabaseLogger:
    """Simple logger that writes entries to a Supabase table."""

    def __init__(self):
        url: str = st.secrets["SUPABASE_URL"]
        key: str = st.secrets["SUPABASE_KEY"]
        self.client: Client = create_client(url, key)

    def log(self, data: Dict):
        """Insert a log record into the 'logs' table."""
        self.client.table("rewriter_logger").insert(data).execute()
