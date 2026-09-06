from fastapi import FastAPI, Request, HTTPException, status, Depends, Query
from contextlib import asynccontextmanager
from typing import Annotated

from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from database import Base, engine, get_ecommerce_db
import models
from schema.product import ProductResponse, PaginatedProductResponse

from routers import cart, orderManage, orders, products, reviews, shippingInformation, users, wishlist

@asynccontextmanager
async def lifespan(_app: FastAPI):
    async with engine.begin() as main_conn:
        await main_conn.run_sync(Base.metadata.create_all)
    yield

    await engine.dispose()

app = FastAPI(lifespan=lifespan)

app.include_router(users.router, prefix='/api/users', tags=['users'])
app.include_router(products.router, prefix='/api/products', tags=['products'])
app.include_router(wishlist.router, prefix='/api/wishlist', tags=['wishlist'])
app.include_router(cart.router, prefix='/api/cart', tags=['cart'])
app.include_router(reviews.router, prefix='/api/reviews', tags=['reviews'])
app.include_router(orderManage.router, prefix='/api/orderManage', tags=['orderManage'])
app.include_router(orders.router, prefix='/api/orders', tags=['orders'])
app.include_router(shippingInformation.router, prefix='/api/shippingInformation', tags=['shippingInformation'])


@app.get('/', include_in_schema=False)
async def home(request: Request):
    return {'message':'Welcome to Ecommerce-Backend'}


@app.get('/search/{search_term}', response_model=PaginatedProductResponse)
async def search_product(
    search_term: str,
    db: Annotated[AsyncSession, Depends(get_ecommerce_db)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=10)] = 10
):
    product_count = await db.execute(
        select(func.count())
        .select_from(models.Product)
        .where(
            or_(
                models.Product.name.icontains(search_term),
                models.Product.description.icontains(search_term)
            )
        )
    )
    total = product_count.scalar() or 0
    
    result = await db.execute(
        select(models.Product)
        .where(
            or_(
                models.Product.name.icontains(search_term),
                models.Product.description.icontains(search_term)
            )
        )
        .offset(skip)
        .limit(limit)
    )

    products = result.scalars().all()

    has_more = skip + len(products) < total
    return PaginatedProductResponse(
        products=[ProductResponse.model_validate(product) for product in products],
        total = total,
        skip = skip,
        limit = limit,
        has_more = has_more
    )
