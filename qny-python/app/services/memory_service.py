from typing import List, Dict
import json
import time
import redis

from ..core.config import settings


_redis = redis.Redis.from_url(settings.redis_url, decode_responses=True)


def _key_ctx(user_id: int, conversation_id: int) -> str:
    return f"chat:ctx:{user_id}:{conversation_id}"


def append_turn(user_id: int, conversation_id: int, role: str, content: str, max_rounds: int = 10) -> None:
    item = json.dumps({"role": role, "content": content, "ts": int(time.time())}, ensure_ascii=False)
    key = _key_ctx(user_id, conversation_id)
    print(f"[DEBUG] Storing to Redis: key={key}, role={role}, content={content[:50]}...")
    _redis.rpush(key, item)
    length = _redis.llen(key)
    print(f"[DEBUG] Redis list length after append: {length}")
    if length > max_rounds * 2:
        _redis.ltrim(key, length - max_rounds * 2, -1)
    _redis.expire(key, 60 * 60 * 24)


def get_recent_context(user_id: int, conversation_id: int, limit: int = 10) -> List[Dict[str, str]]:
    key = _key_ctx(user_id, conversation_id)
    items = _redis.lrange(key, -limit * 2, -1)
    print(f"[DEBUG] Retrieving from Redis: key={key}, found {len(items)} items")
    return [json.loads(x) for x in items]


def clear_context(user_id: int, conversation_id: int) -> None:
    _redis.delete(_key_ctx(user_id, conversation_id))


