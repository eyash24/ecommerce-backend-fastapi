from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import models
from database import get_ecommerce_db
from schema.order import (
    OrderCreate,
    OrderIDResponse,
    OrderUpdate
)

from auth import CurrentUser

router = APIRouter()

@router.get('/{order_manage_id}', response_model=list[OrderIDResponse])
async def get_order(
    order_manage_id: int,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_ecommerce_db)]
):
    result = await db.execute(
        select(models.OrderManage)
        .where(models.OrderManage.id == order_manage_id)
    )
    order_manage = result.scalars().first()

    if not order_manage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Order Manage not found'
        )

    if order_manage.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Not authorised to view order informatoin'
        )

    result = await db.execute(
        select(models.Order)
        .where(models.Order.order_manage_id == order_manage_id)
    )

    orders = result.scalars().all() or []

    return orders

@router.post(
    '/{order_manage_id}', 
    response_model=OrderIDResponse, 
    status_code=status.HTTP_201_CREATED
)
async def create_order(
    order_manage_id: int,
    order_data: OrderCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_ecommerce_db)]
):
    result = await db.execute(
        select(models.OrderManage)
        .where(models.OrderManage.id == order_manage_id)
    )
    order_manage = result.scalars().first()

    if not order_manage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Order Manage not found'
        )

    if order_manage.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Not authorised to create order informatoin'
        )

    new_order = models.Order(
       order_manage_id = order_manage_id,
       product_id = order_data.product_id,
       quantity = order_data.quantity
    )

    db.add(new_order)
    await db.commit()
    await db.refresh(new_order)
    return new_order


@router.patch('/{order_manage_id}/{order_id}', response_model=OrderIDResponse)
async def update_order(
    order_manage_id: int,
    order_id: int,
    order_data: OrderUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_ecommerce_db)]
):
    result = await db.execute(
        select(models.OrderManage)
        .where(models.OrderManage.id == order_manage_id)
    )
    order_manage = result.scalars().first()

    if not order_manage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Order Manage not found'
        )

    if order_manage.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Not authorised to update order informatoin'
        )

    result = await db.execute(
        select(models.Order)
        .where(models.Order.id == order_id)
    )

    order = result.scalars().first()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Order not found'
        )

    order.quantity = order_data.quantity

    db.commit()
    db.refresh(order)
    return order

@router.delete('/{order_manage_id}/{order_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(
    order_manage_id: int,
    order_id: int,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_ecommerce_db)]
):
    result = await db.execute(
        select(models.OrderManage)
        .where(models.OrderManage.id == order_manage_id)
    )
    order_manage = result.scalars().first()

    if not order_manage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Order Manage not found'
        )

    if order_manage.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Not authorised to update order informatoin'
        )

    result = await db.execute(
        select(models.Order)
        .where(models.Order.id == order_id)
    )

    order = result.scalars().first()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Order not found'
        )

    await db.delete(order)
    await db.commit()