from __future__ import annotations
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Float, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(200), nullable=False)
    image_url : Mapped[str] = mapped_column(String(200), nullable=False)
    admin_role: Mapped[bool] = mapped_column(Boolean, default=False)

    reset_tokens : Mapped[list[PasswordResetToken]] = relationship(
        back_populates='user',
        cascade='all, delete-orphan'
    )
    
    wishlist_products : Mapped[list[Wishlist]] = relationship(
        back_populates='user',
        cascade='all, delete-orphan'
    )

    orders : Mapped[list[OrderManage]] = relationship(
        back_populates='user'
    )

    cart : Mapped[list[Cart]] = relationship(
        back_populates='user',
        cascade='all, delete-orphan'
    )

    review : Mapped[list[Review]] = relationship(
        back_populates='user'
    )

    product: Mapped[list[Product]] = relationship(
        back_populates='user',
        cascade='all, delete-orphan'
    )

    shipping_address: Mapped[list[ShipingInformation]] = relationship(
        back_populates='user'
    )


class PasswordResetToken(Base):
    __tablename__ = 'password_reset_token'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )

    user: Mapped[User] = relationship(back_populates='reset_tokens')


    
class Product(Base):
    __tablename__ = 'products'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(Text(500), nullable=True)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    image_url : Mapped[str] = mapped_column(Text(200), nullable=False)
    category : Mapped[str] = mapped_column(String(50), nullable=False)
    inStock: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id'),
        nullable=False,
        index=True,
    ) 

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )

    review : Mapped[list[Review]] = relationship(
        back_populates='products',
        cascade='all, delete-orphan'
    )

    user: Mapped[User] = relationship(back_populates='product')


class Review(Base):
    __tablename__ = 'reviews'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(50), nullable=False)
    rating: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    comment: Mapped[str] = mapped_column(Text(250), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id'),
        nullable=False,
        index=True,
    ) 
    product_id: Mapped[int] = mapped_column(
        ForeignKey('product.id'),
        nullable=False,
        index=True
    )

    product : Mapped[Product] = relationship(back_populates='review')
    user : Mapped[User] = relationship(back_populates='review')



class Wishlist(Base):
    __tablename__ = 'wishlists'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id'),
        nullable=False,
        index=True,
    ) 
    product_id: Mapped[int] = mapped_column(
        ForeignKey('product.id'),
        nullable=False,
        index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )

    user : Mapped[User] = relationship(back_populates='wishlist_products')


class Cart(Base):
    __tablename__ = 'cart'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id'),
        nullable=False,
        index=True,
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey('products.id'),
        nullable=False,
        index=True
    )
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )

    user : Mapped[User] = relationship(back_populates='cart')



class OrderManage(Base):
    __tablename__ = 'orderManage'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    items: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_price: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    payment_status: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    payment_mode: Mapped[str] = mapped_column(String(15), nullable=False, default='stripe')
    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id'),
        nullable=False,
        index=True,
    ) 
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
    shipping_id: Mapped[int] = mapped_column(
        ForeignKey('shipping_infomation.id'),
        nullable=False
    )

    user : Mapped[User] = relationship(back_populates='orders')
    shipping: Mapped[ShipingInformation] = relationship(back_populates='order_manage', cascade='all, delete-orphan')

class Order(Base):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    order_manage_id: Mapped[int] = mapped_column(
        ForeignKey('orders.id'),
        nullable=False,
        index=True
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey('products.id'),
        nullable=False,
        index=True
    )
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)


class ShipingInformation(Base):
    __tablename__ = 'shipping_information'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=True)
    address: Mapped[str] = mapped_column(Text(250), nullable=False)
    city: Mapped[str] = mapped_column(String(50), nullable=False)
    state: Mapped[str] = mapped_column(String(50), nullable=False)
    zip: Mapped[str] = mapped_column(String(10), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id'),
        nullable=False,
        index=True,
    ) 

    user: Mapped[User] = relationship(back_populates='shipping_address')
    order_manage: Mapped[OrderManage] = relationship(back_populates='shipping')