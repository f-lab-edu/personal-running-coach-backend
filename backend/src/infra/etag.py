from hashlib import md5
import json
from fastapi.concurrency import run_in_threadpool
from schemas.models import TrainResponse

def _generate_etag(data) -> str:
    encoded = json.dumps(data, sort_keys=True, separators=(",", ":")).encode()
    return md5(encoded).hexdigest()

async def generate_etag(data) -> str:
    return await run_in_threadpool(_generate_etag, data)

# -------------------- serializing -----------------#

def serialize_train_response(item: TrainResponse) -> dict:
    return {
        "session_id": str(item.session_id),         # UUID -> str
        "train_date": item.train_date.isoformat(),  # datetime -> ISO string
        "distance": item.distance,
        "avg_speed": item.avg_speed,
        "total_time": item.total_time,
        "activity_title": item.activity_title,
        "analysis_result": item.analysis_result,
    }
