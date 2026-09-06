import os
from dotenv import load_dotenv

load_dotenv()


def get_secret(key: str, default: str = "") -> str:
    """Retrieves secret from environment variable or Streamlit st.secrets (supporting all TOML structures)."""
    val = os.getenv(key)
    if not val and key != key.lower():
        val = os.getenv(key.lower())

    if not val:
        try:
            import streamlit as st
            if hasattr(st, "secrets"):
                sec = st.secrets
                # 1. Direct top-level lookup
                if key in sec:
                    val = sec[key]
                elif key.lower() in sec:
                    val = sec[key.lower()]
                # 2. Nested section lookup (e.g. [postgres] or [db] or [groq])
                elif "postgres" in sec:
                    p_sec = sec["postgres"]
                    if isinstance(p_sec, dict) or hasattr(p_sec, "get"):
                        val = p_sec.get(key) or p_sec.get(key.lower()) or p_sec.get("url")
                elif "db" in sec:
                    db_sec = sec["db"]
                    if isinstance(db_sec, dict) or hasattr(db_sec, "get"):
                        val = db_sec.get(key) or db_sec.get(key.lower()) or db_sec.get("url")
                elif "groq" in sec:
                    g_sec = sec["groq"]
                    if isinstance(g_sec, dict) or hasattr(g_sec, "get"):
                        val = g_sec.get(key) or g_sec.get(key.lower()) or g_sec.get("api_key")
        except Exception as e:
            print(f"Warning: st.secrets lookup for {key} encountered error ({e})")

    return str(val).strip() if val else default


GROQ_API_KEY = get_secret("GROQ_API_KEY", "")
DATABASE_URL = get_secret("DATABASE_URL", "postgresql://postgres:poorvi@localhost:5434/health_twin")
HOST = get_secret("HOST", "0.0.0.0")
PORT = int(get_secret("PORT", "8000"))
