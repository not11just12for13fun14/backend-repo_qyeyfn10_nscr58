import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import db, create_document, get_documents

app = FastAPI(title="Retro Blog API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CreateCategory(BaseModel):
    name: str
    slug: str
    color: Optional[str] = None

class CreateTag(BaseModel):
    name: str
    slug: str

class CreatePost(BaseModel):
    title: str
    slug: str
    excerpt: Optional[str] = None
    content: str
    cover_image: Optional[str] = None
    category: str
    tags: List[str] = []
    author: Optional[str] = None
    published: bool = True

@app.get("/")
async def read_root():
    return {"message": "Retro Blog API running"}

@app.get("/schema")
async def read_schema():
    # Expose schemas so the integrated DB viewer can introspect
    try:
        import schemas
        return {name: getattr(schemas, name).model_json_schema() for name in dir(schemas) if hasattr(getattr(schemas, name), 'model_json_schema')}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test")
async def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set",
        "database_name": "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set",
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"
    return response

# ----- Category Endpoints -----
@app.post("/api/categories")
async def create_category(payload: CreateCategory):
    existing = db["category"].find_one({"slug": payload.slug}) if db else None
    if existing:
        raise HTTPException(status_code=400, detail="Category slug already exists")
    inserted_id = create_document("category", payload.model_dump())
    return {"id": inserted_id}

@app.get("/api/categories")
async def list_categories():
    items = get_documents("category")
    return items

# ----- Tag Endpoints -----
@app.post("/api/tags")
async def create_tag(payload: CreateTag):
    existing = db["tag"].find_one({"slug": payload.slug}) if db else None
    if existing:
        raise HTTPException(status_code=400, detail="Tag slug already exists")
    inserted_id = create_document("tag", payload.model_dump())
    return {"id": inserted_id}

@app.get("/api/tags")
async def list_tags():
    items = get_documents("tag")
    return items

# ----- Post Endpoints -----
@app.post("/api/posts")
async def create_post(payload: CreatePost):
    if db:
        cat = db["category"].find_one({"slug": payload.category})
        if not cat:
            raise HTTPException(status_code=400, detail="Category does not exist")
        # optional: validate tags exist
        for t in payload.tags:
            if not db["tag"].find_one({"slug": t}):
                raise HTTPException(status_code=400, detail=f"Tag '{t}' does not exist")
    inserted_id = create_document("post", payload.model_dump())
    return {"id": inserted_id}

@app.get("/api/posts")
async def list_posts(
    category: Optional[str] = None,
    tag: Optional[str] = None,
    q: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100)
):
    filter_dict = {"published": True}
    if category:
        filter_dict["category"] = category
    if tag:
        filter_dict["tags"] = tag
    if q:
        # simple contains search on title/excerpt
        filter_dict["$or"] = [
            {"title": {"$regex": q, "$options": "i"}},
            {"excerpt": {"$regex": q, "$options": "i"}},
        ]
    items = get_documents("post", filter_dict, limit)
    return items

@app.get("/api/posts/{slug}")
async def get_post(slug: str):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")
    doc = db["post"].find_one({"slug": slug})
    if not doc:
        raise HTTPException(status_code=404, detail="Post not found")
    # Convert ObjectId
    doc["_id"] = str(doc["_id"])
    return doc

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
