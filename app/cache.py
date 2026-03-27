import os, logging
from unittest.mock import MagicMock

logger = logging.getLogger(__name__)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

def create_redis_client():
    try:
        import redis
        client = redis.from_url(REDIS_URL, decode_responses=True, socket_connect_timeout=1)
        client.ping()
        logger.info(f"Redis connecté: {REDIS_URL}")
        return client
    except Exception as e:
        logger.warning(f"Redis indisponible ({e}). MagicMock activé.")
        mock = MagicMock()
        mock.get.return_value = None # <-- LA CORRECTION EST LÀ : get() retourne toujours None
        return mock

redis_client = create_redis_client()

# --- Les 3 fonctions manquantes pour products.py ---
def get_cached(key: str):
    try: return redis_client.get(key)
    except: return None

def set_cached(key: str, value: str, ttl: int = 300):
    try: redis_client.setex(key, ttl, value)
    except: pass

def delete_cached(key: str):
    try: redis_client.delete(key)
    except: pass