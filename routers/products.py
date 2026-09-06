from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Query,
    HTTPException,
    status
)

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

import models
from database import get_ecommerce_db
from schema.product import (
    ProductResponse,
    ProductCreate,
    ProductStatus,
    ProductUpdate,
    PaginatedProductResponse,
    ProductCategoryResponse
)
from schema.review import PaginatedReviewResponse, ReviewResponse

from auth import CurrentUser


router = APIRouter()

@router.get(
    '/{product_id}',
    response_model=ProductResponse
)
async def get_product_id(
    product_id: int,
    db: Annotated[AsyncSession, Depends(get_ecommerce_db)]
):
    result = await db.execute(
        select(models.Product)
        .where(models.Product.id == product_id)
    )
    product_info = result.scalars().first()
    if not product_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Product not found'
        )

    return product_info

@router.get(
    '/all/proc',
    response_model=PaginatedProductResponse
)
async def get_products_all(
    db: Annotated[AsyncSession, Depends(get_ecommerce_db)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1,le=100)] = 10
):
    product_count = await db.execute(
        select(func.count())
        .select_from(models.Product)
    )
    total = product_count.scalar() or 0
    
    result = await db.execute(
        select(models.Product)
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

@router.get(
    '/all/categories',
    response_model=ProductCategoryResponse
)
async def get_product_category_list(
    db: Annotated[AsyncSession, Depends(get_ecommerce_db)]
):
    result = await db.execute(
        select(models.Product.category).distinct()
    )
    category_list = result.scalars().all() or []

    return ProductCategoryResponse(
        categories=category_list
    )



@router.post(
    '',
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_product(
    product_data: ProductCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_ecommerce_db)]
):
    new_product = models.Product(
        name = product_data.name,
        description = product_data.description,
        price = product_data.price,
        image_url = product_data.image_url,
        category = product_data.category,
        quantity = product_data.quantity,
        inStock = True if product_data.quantity > 0 else False,
        user_id = current_user.id
    )

    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)
    return new_product

@router.put('/{product_id}', response_model=ProductResponse)
async def update_product_full(
    product_id: int,
    product_data: ProductUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_ecommerce_db)]
):
    result = await db.execute(
        select(models.Product)
        .where(models.Product.id == product_id)
    )

    product = result.scalars().first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Product not found'
        )

    if product.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Not authorised to update product information'
        )

    product.name = product_data.name
    product.description = product_data.description
    product.price = product_data.price
    product.image_url = product_data.image_url
    product.category = product_data.category
    product.quantity = product_data.quantity
    product.inStock = True if product_data.quantity > 0 else False

    await db.commit()
    await db.refresh(product)
    return product

@router.patch('/{product_id}', response_model=ProductResponse)
async def update_product_partial(
    product_id: int,
    product_data: ProductUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_ecommerce_db)]
):
    result = await db.execute(
        select(models.Product)
        .where(models.Product.id == product_id)
    )

    product = result.scalars().first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Product not found'
        )

    if product.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Not authorised to update product information'
        )

    update_data = product_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)

    if product_data.quantity is not None:
        product.inStock = True if product_data.quantity > 0 else False

    await db.commit()
    await db.refresh(product)
    return product

@router.delete('/{product_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_ecommerce_db)]
):
    result = await db.execute(
        select(models.Product)
        .where(models.Product.id == product_id)
    )

    product = result.scalars().first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Product not found'
        )

    if product.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Not authorised to delete product information'
        )

    await db.delete(product)
    await db.commit()


@router.get(
    '/category/{category}',
    response_model=PaginatedProductResponse
)
async def get_product_category(
    category: str,
    db: Annotated[AsyncSession, Depends(get_ecommerce_db)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1,le=100)] = 10
):
    product_count = await db.execute(
        select(func.count())
        .select_from(models.Product)
        .where(models.Product.category == category)
    )
    total = product_count.scalar() or 0
    
    result = await db.execute(
        select(models.Product)
        .where(models.Product.category == category)
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

@router.get(
    '/instock/{product_id}',
    response_model=ProductStatus
)
async def get_product_status(
    product_id: int,
    db: Annotated[AsyncSession, Depends(get_ecommerce_db)]
):
    result = await db.execute(
        select(models.Product)
        .where(models.Product.id == product_id)
    )

    product = result.scalars().first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Product not found'
        )

    return ProductStatus(
        inStock=product.inStock
    )


@router.get(
    '/reviews/{product_id}'
)
async def get_product_reviews(
    product_id: int,
    db: Annotated[AsyncSession, Depends(get_ecommerce_db)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=10)] = 10
):
    review_count = await db.execute(
        select(func.count())
        .select_from(models.Review)
        .where(models.Review.product_id == product_id)
    )

    total = review_count.scalar() or 0

    result = await db.execute(
        select(models.Review)
        .where(models.Review.product_id == product_id)
        .order_by(models.Review.created_at.desc())
        .offset(skip)
        .limit(limit)
    )

    reviews = result.scalars().all() or []
    print(reviews)

    has_more = skip + len(reviews) < total

    return PaginatedReviewResponse(
        reviews=[ReviewResponse.model_validate(review) for review in reviews],
        total = total,
        skip = skip,
        limit = limit,
        has_more = has_more
    )

