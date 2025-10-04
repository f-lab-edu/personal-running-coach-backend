from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from interfaces.api import routers
from config import settings
from infra.db.storage.session import create_db_and_tables, close_db
from infra.db.redis.redis_client import init_redis, close_redis

@asynccontextmanager
async def lifespan(app:FastAPI):
    ## db 시작
    await create_db_and_tables()
    await init_redis()
    yield
    ## db 종료
    await close_db()
    await close_redis()


app = FastAPI(lifespan=lifespan)
for r in routers:
    app.include_router(r, prefix="/api") # nginx /api/ 

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors.origins,
    allow_credentials=settings.cors.credentials,
    allow_methods=settings.cors.methods,
    allow_headers=settings.cors.headers,
)
    
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.web.host, port=settings.web.port, reload=True)