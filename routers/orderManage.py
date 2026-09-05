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
    OrderManageCreate,
    OrderManageIDResponse,
    OrderManageUpdate
)

from auth import CurrentUser

router = APIRouter()

@router.get(
    '{order_manage_id}',
    response_model=OrderManageIDResponse
)
async def get_order_manage_id(
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
            detail='Not authorised to view order manage information'
        )

    return order_manage


@router.post('', response_model=OrderManageIDResponse, status_code=status.HTTP_201_CREATED)
async def create_order_manage(
    current_user: CurrentUser,
    order_manage_data: OrderManageCreate,
    db: Annotated[AsyncSession, Depends(get_ecommerce_db)]
):
    result = await db.execute(
        select(models.ShipingInformation)
        .where(models.ShipingInformation.id == order_manage_data.shipping_id)
    )

    shipping_info = result.scalars().first()

    if not shipping_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Order Manage Shipping Id not found'
        )
    
    new_order_manage = models.OrderManage(
        items = order_manage_data.items,
        total_price = order_manage_data.total_price,
        payment_status = order_manage_data.payment_status,
        payment_mode = order_manage_data.payment_mode,
        user_id = current_user.id,
        shipping_id = order_manage_data.shipping_id
    )

    db.add(new_order_manage)
    await db.commit()
    await db.refresh(new_order_manage)
    return new_order_manage   

@router.put(
    '/{order_manage_id}',
    response_models=OrderManageIDResponse
)
async def update_order_manage_full(
    order_manage_id: int,
    current_user: CurrentUser,
    order_manage_data: OrderManageUpdate,
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
            detail='Order Manage Shipping Id not found'
        )

    if order_manage.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Not authorised to update order manage information'
        )

    result = await db.execute(
        select(models.ShipingInformation)
        .where(
            models.ShipingInformation.id == order_manage_data.shipping_id,
        )
    )

    shipping = result.scalars().first()

    if not shipping:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Order Manage Shipping Id not found'
        )

    if shipping.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Not authorised to utilise this shipping information'
        ) 

    order_manage.items = order_manage_data.items
    order_manage.total_price = order_manage_data.total_price
    order_manage.payment_status = order_manage_data.payment_status
    order_manage.payment_mode = order_manage_data.payment_mode
    order_manage.user_id = current_user.id
    order_manage.shipping_id = order_manage_data.shipping_id

    await db.commit()
    await db.refresh(order_manage)
    return order_manage


@router.patch(
    '/{order_manage_id}',
    response_models=OrderManageIDResponse
)
async def update_order_manage_partial(
    order_manage_id: int,
    current_user: CurrentUser,
    order_manage_data: OrderManageUpdate,
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
            detail='Order Manage Shipping Id not found'
        )

    if order_manage.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Not authorised to update order manage information'
        )

    if order_manage_data.shipping_id is not None:
        result = await db.execute(
            select(models.ShipingInformation)
            .where(
                models.ShipingInformation.id == order_manage_data.shipping_id,
            )
        )

        shipping = result.scalars().first()

        if not shipping:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Order Manage Shipping Id not found'
            )

        if shipping.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Not authorised to utilise this shipping information'
            )

    update_data = order_manage_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(order_manage, field, value)

    await db.commit()
    await db.refresh(order_manage)
    return order_manage

@router.delete(
    '/{order_manage_id}',
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_order_manage(
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
            detail='Order Manage Shipping Id not found'
        )

    if order_manage.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Not authorised to update order manage information'
        )

    await db.delete(order_manage)
    await db.commit()