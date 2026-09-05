from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Query,
    HTTPException,
    status
)

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import models
from database import get_ecommerce_db
from schema.shipping_information import (
    ShippingInformationCreate,
    ShippingInformatinUpdate,
    ShippingInformationResponse
)

from auth import CurrentUser


router = APIRouter()

@router.get(
    '/{shipping_id}',
    response_models=ShippingInformationResponse
)
async def get_shipping_info(
    shipping_id: int,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_ecommerce_db)]
):
    result = await db.execute(
        select(models.ShipingInformation)
        .where(models.ShipingInformation.id == shipping_id)
    )
    shipping_info = result.scalars().first()

    if not shipping_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Shipping Information not found'
        )

    if shipping_info.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Not authorised to view shipping informatoin'
        )

    return shipping_info

@router.post(
    '',
    response_model=ShippingInformationResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_shipping_information(
    shipping_info: ShippingInformationCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_ecommerce_db)]
):
    new_shipping_info = models.ShipingInformation(
        first_name = shipping_info.first_name,
        last_name = shipping_info.last_name,
        address = shipping_info.address,
        city = shipping_info.city,
        state = shipping_info.state,
        zip = shipping_info.zip,
        user_id = current_user.id
    )

    db.add(new_shipping_info)
    await db.commit()
    await db.refresh(new_shipping_info)
    return new_shipping_info

@router.put(
    '/{shipping_id}',
    response_model=ShippingInformationResponse
)
async def update_shipping_information_full(
    shipping_id: int,
    shipping_data: ShippingInformatinUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_ecommerce_db)]
):
    result = await db.execute(
        select(models.ShipingInformation)
        .where(models.ShipingInformation.id == shipping_id)
    )

    shipping_info = result.scalars().first()

    if not shipping_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Shipping information not found'
        )

    if shipping_info.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Not authorised to update shippping information'
        )

    shipping_info.first_name = shipping_data.first_name
    shipping_info.last_name = shipping_data.last_name
    shipping_info.address = shipping_data.address
    shipping_info.city = shipping_data.city
    shipping_info.state = shipping_data.state
    shipping_info.zip = shipping_data.zip

    await db.commit()
    await db.refresh(shipping_info)
    return shipping_info

@router.patch(
    '/{shipping_id}',
    response_model=ShippingInformationResponse
)
async def update_shipping_information_partial(
    shipping_id: int,
    shipping_data: ShippingInformatinUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_ecommerce_db)]
):
    result = await db.execute(
        select(models.ShipingInformation)
        .where(models.ShipingInformation.id == shipping_id)
    )

    shipping_info = result.scalars().first()

    if not shipping_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Shipping information not found'
        )

    if shipping_info.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Not authorised to update shippping information'
        )

    update_data = shipping_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(shipping_info, field, value)

    await db.commit()
    await db.refresh(shipping_info)
    return shipping_info

@router.delete(
    '/{shipping_id}',
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_shipping_information(
    shipping_id: int,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_ecommerce_db)]
):
    result = await db.execute(
        select(models.ShipingInformation)
        .where(models.ShipingInformation.id == shipping_id)
    )

    shipping_info = result.scalars().first()

    if not shipping_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Shipping information not found'
        )

    if shipping_info.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Not authorised to delete shippping information'
        )

    await db.delete(shipping_info)
    await db.commit()