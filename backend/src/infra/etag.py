import hashlib
import json
from fastapi.concurrency import run_in_threadpool

def _generate_etag(data: str) -> str:
    encoded = json.dumps(data, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.md5(encoded).hexdigest()

async def generate_etag(data:str) -> str:
    return await run_in_threadpool(_generate_etag, data)