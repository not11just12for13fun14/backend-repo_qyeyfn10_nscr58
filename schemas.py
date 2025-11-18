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
from typing import Optional, List

# Example schemas (replace with your own):

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

# Retro Blog Schemas
# --------------------------------------------------
class Category(BaseModel):
    name: str = Field(..., description="Category name")
    slug: str = Field(..., description="URL-friendly slug")
    color: Optional[str] = Field(None, description="Hex color for UI accents")

class Tag(BaseModel):
    name: str = Field(..., description="Tag label")
    slug: str = Field(..., description="URL-friendly slug")

class Post(BaseModel):
    title: str = Field(..., description="Post title")
    slug: str = Field(..., description="URL-friendly slug")
    excerpt: Optional[str] = Field(None, description="Short description")
    content: str = Field(..., description="Markdown or HTML content")
    cover_image: Optional[str] = Field(None, description="Cover image URL")
    category: str = Field(..., description="Category slug")
    tags: List[str] = Field(default_factory=list, description="List of tag slugs")
    author: Optional[str] = Field(None, description="Author name")
    published: bool = Field(True, description="Whether the post is published")

# Note: The Flames database viewer will automatically:
# 1. Read these schemas from GET /schema endpoint
# 2. Use them for document validation when creating/editing
# 3. Handle all database operations (CRUD) directly
# 4. You don't need to create any database endpoints!
