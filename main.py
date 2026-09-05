from fastapi import FastAPI, Request, HTTPException, status, Depends
from contextlib import asynccontextmanager

from datetime import datetime, UTC

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import Base, engine, get_ecommerce_db

@asynccontextmanager
async def lifespan(_app: FastAPI):
    async with engine.begin() as main_conn:
        await main_conn.run_sync(Base.metadata.create_all)
    yield

    await engine.dispose()

app = FastAPI(lifespan=lifespan)

app.get('/', include_in_schema=False)
async def home(request: Request):
    return {'message':'Welcome to Ecommerce-Backend'}

