import os
from dotenv import load_dotenv

load_dotenv()


def get_secret(key: str, default: str = "") -> str:
    """Retrieves secret from environment variable or Streamlit st.secrets."""
    val = os.getenv(key)
    if not val:
        try:
            import streamlit as st
            if key in st.secrets:
                val = st.secrets[key]
        except Exception:
            pass
    return val or default


GROQ_API_KEY = get_secret("GROQ_API_KEY", "")
DATABASE_URL = get_secret("DATABASE_URL", "postgresql://postgres:poorvi@localhost:5434/health_twin")
HOST = get_secret("HOST", "0.0.0.0")
PORT = int(get_secret("PORT", "8000"))
