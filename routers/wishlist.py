from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Query,
    HTTPException,
    status
)

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

import models
from database import get_ecommerce_db
from schema.product import (
    ProductResponse,
    PaginatedProductResponse
)
from schema.wishlist import (
    WishlistCreate,
    WishlistResponse
)

from auth import CurrentUser


router = APIRouter()

@router.get(
    '/ids',
    response_model=list[WishlistResponse]
)
async def get_wishlist_product_id(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_ecommerce_db)]
):
    result = await db.execute(
        select(models.Wishlist)
        .where(models.Wishlist.user_id == current_user.id)
    )

    wishlist_items = result.scalars().all() or []

    return wishlist_items


@router.get(
    '/items',
    response_model=PaginatedProductResponse
)
async def get_wishlist_product(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_ecommerce_db)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=10)] = 10
):
    total = await db.scalar(
        select(func.count())
        .select_from(models.Wishlist)
        .where(models.Wishlist.user_id == current_user.id)
    ) or 0

    result = await db.execute(
        select(models.Product)
        .join(
            models.Wishlist,
            models.Wishlist.product_id == models.Product.id
        )
        .where(
            models.Wishlist.user_id == current_user.id
        )
        .order_by(models.Wishlist.created_at.desc())
        .offset(skip)
        .limit(limit)
    )

    products = result.scalars().all()

    has_more = skip + len(products) < total

    return PaginatedProductResponse(
        products=[
            ProductResponse.model_validate(product)
            for product in products
        ],
        total=total,
        skip=skip,
        limit=limit,
        has_more=has_more
    )


@router.post('', status_code=status.HTTP_201_CREATED, response_model=WishlistResponse)
async def create_wishlist(
    wishlist_data: WishlistCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_ecommerce_db)]
):
    result = await db.execute(
        select(models.Wishlist)
        .where(
            models.Wishlist.user_id == current_user.id,
            models.Wishlist.product_id == wishlist_data.product_id
        )
    )

    wishlist = result.scalars().first()

    if wishlist:
        return wishlist

    new_wishlist = models.Wishlist(
        user_id = current_user.id,
        product_id = wishlist_data.product_id
    )

    db.add(new_wishlist)
    await db.commit()
    await db.refresh(new_wishlist)
    return new_wishlist


@router.delete('/{product_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_wishlist(
    product_id: int,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_ecommerce_db)]
):
    result = await db.execute(
        select(models.Wishlist)
        .where(
            models.Wishlist.user_id == current_user.id,
            models.Wishlist.product_id == product_id
        )
    )

    wishlist = result.scalars().first()

    if not wishlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Product does not exist in Wishlist'
        )

    await db.delete(wishlist)
    await db.commit()

