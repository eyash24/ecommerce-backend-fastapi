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
from schema.review import (
    ReviewResponse,
    ReviewCreate,
    ReviewUpdate
)

from auth import CurrentUser


router = APIRouter()

@router.get(
    '/{review_id}',
    response_model=ReviewResponse
)
async def get_review_id(
    review_id: int,
    db: Annotated[AsyncSession, Depends(get_ecommerce_db)]
):
    result = await db.execute(
        select(models.Review)
        .where(models.Review.id == review_id)
    )

    review_info = result.scalars().first()
    if not review_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Review not found'
        )

    return review_info

@router.post(
    '',
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_review(
    review_data: ReviewCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_ecommerce_db)]
):
    new_review = models.Review(
        title = review_data.title,
        rating = review_data.rating,
        comment = review_data.comment,
        user_id = current_user.id,
        product_id = review_data.product_id
    )

    db.add(new_review)
    await db.commit()
    await db.refresh(new_review)
    return new_review


@router.put('/{review_id}', response_model=ReviewResponse)
async def update_review_full(
    review_id: int,
    review_data: ReviewUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_ecommerce_db)]
):
    result = await db.execute(
        select(models.Review)
        .where(models.Review.id == review_id)
    )

    review = result.scalars().first()
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Review not found'
        )

    if review.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Not authorised to update review information'
        )
    
    review.title = review_data.title
    review.rating = review_data.rating
    review.comment = review_data.comment

    await db.commit()
    await db.refresh(review)
    return review    

@router.patch('/{review_id}', response_model=ReviewResponse)
async def update_review_partial(
    review_id: int,
    review_data: ReviewUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_ecommerce_db)]
):
    result = await db.execute(
        select(models.Review)
        .where(models.Review.id == review_id)
    )

    review = result.scalars().first()
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Review not found'
        )

    if review.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Not authorised to update review information'
        )
    
    update_data = review_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(review, field, value)

    await db.commit()
    await db.refresh(review)
    return review

@router.delete('/{review_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    review_id: int,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_ecommerce_db)]
):
    result = await db.execute(
        select(models.Review)
        .where(models.Review.id == review_id)
    )

    review = result.scalars().first()
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Review not found'
        )

    if review.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Not authorised to delete review information'
        )

    await db.delete(review)
    await db.commit()