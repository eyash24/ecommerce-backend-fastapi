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
    ProductResponse
)
from schema.cart import (
    CartProductResponse,
    CartCreate,
    CartUpdate,
    CartIDResponse
)

from auth import CurrentUser

router = APIRouter()

@router.get('/ids', response_model=list[CartIDResponse])
async def get_cart_product_id(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_ecommerce_db)]
):
    result = await db.execute(
        select(models.Cart)
        .where(models.Cart.user_id == current_user.id)
    )

    cart_product_id = result.scalars().all() or []

    return cart_product_id


@router.get('/items', response_model=list[CartProductResponse])
async def get_cart_products(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_ecommerce_db)]
):
    result = await db.execute(
        select(models.Cart, models.Product)
        .join(
            models.Product,
            models.Product.id == models.Cart.product_id
        )
        .where(models.Cart.user_id == current_user.id)
        .order_by(models.Cart.created_at.desc())
    )

    cart_products = result.all()

    return [
        CartProductResponse(
            id=cart.id,
            product=product,
            quantity=cart.quantity,
            created_at=cart.created_at,
            user_id=current_user.id
        )
        for cart, product in cart_products
    ]

@router.post('', response_model=CartIDResponse, status_code=status.HTTP_201_CREATED)
async def create_cart_product_id(
    cart_data: CartCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_ecommerce_db)]
):
    result = await db.execute(
        select(models.Product)
        .where(models.Product.id == cart_data.product_id)
    )
    product = result.scalars().first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Product not found'
        )
    
    new_cart_rec = models.Cart(
        user_id=current_user.id,
        product_id=cart_data.product_id,
        quantity=cart_data.quantity
    )

    db.add(new_cart_rec)
    await db.commit()
    await db.refresh(new_cart_rec)
    return new_cart_rec

@router.patch('/{product_id}', response_model=CartIDResponse)
async def update_cart(
    product_id: int,
    cart_data: CartUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_ecommerce_db)]
):
    result = await db.execute(
        select(models.Cart)
        .where(
            models.Cart.product_id == product_id,
            models.Cart.user_id == current_user.id
        )
    )

    cart = result.scalars().first()

    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Cart Product not found'
        )

    cart.quantity = cart_data.quantity

    db.commit()
    db.refresh(cart)
    return cart

@router.delete('/{product_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_cart(
    product_id: int,
    cart_data: CartUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_ecommerce_db)]
):
    result = await db.execute(
        select(models.Cart)
        .where(
            models.Cart.product_id == product_id,
            models.Cart.user_id == current_user.id
        )
    )

    cart = result.scalars().first()

    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Cart Product not found'
        )


    await db.delete(cart)
    await db.commit()
