import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import db, create_document, get_documents
from schemas import (
    Product, Category, Sector, News, Document as Doc, Job,
    Application, ContactMessage, CompanyProfile
)

app = FastAPI(title="Chemical Company API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Chemical Company API running"}


# Utility: serialize Mongo docs (ObjectId not needed for read-only lists here)
def _serialize_list(items):
    for it in items:
        it.pop("_id", None)
    return items


# --------------------------- Catalog Endpoints ---------------------------
@app.get("/api/categories", response_model=List[Category])
def list_categories():
    items = get_documents("category")
    return _serialize_list(items)


@app.get("/api/products", response_model=List[Product])
def list_products(category: Optional[str] = None, q: Optional[str] = None):
    flt = {}
    if category:
        flt["category"] = category
    if q:
        flt["$or"] = [
            {"name": {"$regex": q, "$options": "i"}},
            {"summary": {"$regex": q, "$options": "i"}},
            {"description": {"$regex": q, "$options": "i"}},
            {"keywords": {"$regex": q, "$options": "i"}},
        ]
    items = get_documents("product", flt)
    return _serialize_list(items)


@app.get("/api/products/{slug}", response_model=Product)
def get_product(slug: str):
    items = get_documents("product", {"slug": slug}, limit=1)
    if not items:
        raise HTTPException(status_code=404, detail="Product not found")
    item = items[0]
    item.pop("_id", None)
    return item


@app.get("/api/sectors", response_model=List[Sector])
def list_sectors():
    items = get_documents("sector")
    return _serialize_list(items)


@app.get("/api/sectors/{slug}", response_model=Sector)
def get_sector(slug: str):
    items = get_documents("sector", {"slug": slug}, limit=1)
    if not items:
        raise HTTPException(status_code=404, detail="Sector not found")
    item = items[0]
    item.pop("_id", None)
    return item


# --------------------------- Content Endpoints ---------------------------
@app.get("/api/news", response_model=List[News])
def list_news(tag: Optional[str] = None):
    flt = {"tags": tag} if tag else {}
    items = get_documents("news", flt)
    return _serialize_list(items)


@app.get("/api/documents", response_model=List[Doc])
def list_documents(product: Optional[str] = None, category: Optional[str] = None, language: Optional[str] = None):
    flt = {}
    if product:
        flt["product_slug"] = product
    if category:
        flt["category"] = category
    if language:
        flt["language"] = language
    items = get_documents("document", flt)
    return _serialize_list(items)


# --------------------------- Careers Endpoints ---------------------------
@app.get("/api/jobs", response_model=List[Job])
def list_jobs(department: Optional[str] = None):
    flt = {"department": department} if department else {}
    items = get_documents("job", flt)
    return _serialize_list(items)


class ApplicationResponse(BaseModel):
    status: str


@app.post("/api/applications", response_model=ApplicationResponse)
def submit_application(payload: Application):
    create_document("application", payload)
    return {"status": "ok"}


# --------------------------- Contact Endpoints ---------------------------
class ContactResponse(BaseModel):
    status: str


@app.post("/api/contact", response_model=ContactResponse)
def submit_contact(payload: ContactMessage):
    create_document("contactmessage", payload)
    return {"status": "ok"}


# --------------------------- Company Profile ---------------------------
@app.get("/api/company", response_model=CompanyProfile | dict)
def get_company():
    items = get_documents("companyprofile", limit=1)
    if not items:
        return {"company_name": "Azienda Chimica"}
    item = items[0]
    item.pop("_id", None)
    return item


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
