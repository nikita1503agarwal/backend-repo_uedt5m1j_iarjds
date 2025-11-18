"""
Database Schemas for the Chemical Company CMS

Each Pydantic model represents a MongoDB collection. The collection name is the
lowercased class name (e.g., Product -> "product").

These schemas are used for request validation and to describe the structure
of the CMS used by the website (products, sectors, news, resources, jobs, etc.).
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date


class Category(BaseModel):
    """
    Product categories
    Examples: "chimici per conceria", "specialità chimiche", "fine chemicals"
    """
    name: str = Field(..., description="Category name")
    slug: str = Field(..., description="URL-friendly identifier")
    description: Optional[str] = Field(None, description="Short description")


class Product(BaseModel):
    """Products and solutions"""
    name: str = Field(..., description="Product name")
    slug: str = Field(..., description="URL-friendly identifier")
    category: str = Field(..., description="Category slug")
    summary: Optional[str] = Field(None, description="Short technical overview")
    description: Optional[str] = Field(None, description="Detailed description")
    applications: Optional[List[str]] = Field(default_factory=list, description="Applications/uses")
    benefits: Optional[List[str]] = Field(default_factory=list, description="Key benefits")
    sectors: Optional[List[str]] = Field(default_factory=list, description="Related sectors (slugs)")
    documentation_urls: Optional[List[str]] = Field(default_factory=list, description="Links to PDFs / datasheets")
    keywords: Optional[List[str]] = Field(default_factory=list, description="Search keywords")
    image_url: Optional[str] = Field(None, description="Illustrative image URL")


class Sector(BaseModel):
    """Served industries/markets"""
    name: str = Field(..., description="Sector name")
    slug: str = Field(..., description="URL-friendly identifier")
    challenges: Optional[List[str]] = Field(default_factory=list)
    needs: Optional[List[str]] = Field(default_factory=list)
    solutions: Optional[List[str]] = Field(default_factory=list)
    outcomes: Optional[List[str]] = Field(default_factory=list)
    image_url: Optional[str] = Field(None)


class News(BaseModel):
    """News, articles, press releases"""
    title: str
    slug: str
    excerpt: Optional[str] = None
    content: Optional[str] = None
    cover_image_url: Optional[str] = None
    published_at: Optional[date] = None
    tags: Optional[List[str]] = Field(default_factory=list)


class Document(BaseModel):
    """Downloadable resources (datasheets, catalogs, certifications)"""
    title: str
    description: Optional[str] = None
    url: str = Field(..., description="Absolute URL to the document (PDF)")
    category: Optional[str] = Field(None, description="e.g., datasheet, catalog, certification")
    product_slug: Optional[str] = None
    language: Optional[str] = Field("it", description="Document language code")


class Job(BaseModel):
    """Open positions"""
    title: str
    slug: str
    location: Optional[str] = None
    department: Optional[str] = None
    type: Optional[str] = Field(None, description="Full-time, Internship, etc.")
    description: Optional[str] = None
    requirements: Optional[List[str]] = Field(default_factory=list)


class Application(BaseModel):
    """Job applications or spontaneous applications"""
    name: str
    email: str
    phone: Optional[str] = None
    job_slug: Optional[str] = Field(None, description="Related job slug if applying for a posted role")
    message: Optional[str] = None
    cv_url: Optional[str] = Field(None, description="Link to CV stored elsewhere")
    linkedin_url: Optional[str] = None


class ContactMessage(BaseModel):
    """Contact form submissions"""
    name: str
    email: str
    phone: Optional[str] = None
    company: Optional[str] = None
    subject: Optional[str] = None
    message: str
    topic: Optional[str] = Field(None, description="commerciale, tecnico, altro")


# Optional company profile schema (for CMS-managed company data)
class CompanyProfile(BaseModel):
    company_name: str
    mission: Optional[str] = None
    vision: Optional[str] = None
    values: Optional[List[str]] = Field(default_factory=list)
    history: Optional[str] = None
    facilities: Optional[List[str]] = Field(default_factory=list, description="Plants, labs, capabilities")
    locations: Optional[List[str]] = Field(default_factory=list)
    quality_approach: Optional[str] = None
    safety_approach: Optional[str] = None
    innovation_approach: Optional[str] = None
