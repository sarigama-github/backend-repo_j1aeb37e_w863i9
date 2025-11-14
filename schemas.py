"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

# Example schemas (you can keep these for reference):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Car Wash Franchise Schemas
# --------------------------------------------------

class Plan(BaseModel):
    """Subscription plan details (collection: plan)"""
    name: str
    description: Optional[str] = None
    price_monthly: float = Field(..., ge=0)
    price_yearly: float = Field(..., ge=0)
    washes_per_month: int = Field(..., ge=1)
    popular: bool = False

class Subscription(BaseModel):
    """Customer subscriptions (collection: subscription)"""
    customer_name: str
    email: str
    phone: Optional[str] = None
    vehicle: Optional[str] = None
    plan_name: str
    billing_cycle: Literal["monthly", "yearly"] = "monthly"
    status: Literal["pending", "active", "cancelled"] = "pending"
    start_date: Optional[datetime] = None
    notes: Optional[str] = None

class Lead(BaseModel):
    """Marketing leads captured from landing page (collection: lead)"""
    name: str
    email: str
    phone: Optional[str] = None
    message: Optional[str] = None
