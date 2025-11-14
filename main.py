import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

from database import db, create_document, get_documents
from schemas import Plan, Subscription, Lead

app = FastAPI(title="Car Wash Franchise API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Car Wash Franchise Backend Running"}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
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


# ---------- Car Wash Domain Endpoints ----------

# Seed default plans if none exist
DEFAULT_PLANS = [
    Plan(
        name="Express",
        description="Quick exterior wash. Perfect for a fast shine.",
        price_monthly=19.0,
        price_yearly=190.0,
        washes_per_month=4,
        popular=False,
    ),
    Plan(
        name="Premium",
        description="Exterior + interior vacuum and wipe down.",
        price_monthly=39.0,
        price_yearly=390.0,
        washes_per_month=6,
        popular=True,
    ),
    Plan(
        name="Ultimate",
        description="Full service with wax and wheel detail.",
        price_monthly=59.0,
        price_yearly=590.0,
        washes_per_month=8,
        popular=False,
    ),
]


@app.get("/plans", response_model=List[Plan])
def get_plans():
    if db is None:
        # Return defaults in stateless environments, still useful for demo
        return [p for p in DEFAULT_PLANS]

    count = db["plan"].count_documents({})
    if count == 0:
        # seed defaults
        for plan in DEFAULT_PLANS:
            try:
                create_document("plan", plan)
            except Exception:
                pass

    docs = get_documents("plan")
    # Map to Plan models (ignore extra fields)
    plans = []
    for d in docs:
        try:
            plans.append(
                Plan(
                    name=d.get("name"),
                    description=d.get("description"),
                    price_monthly=float(d.get("price_monthly")),
                    price_yearly=float(d.get("price_yearly")),
                    washes_per_month=int(d.get("washes_per_month")),
                    popular=bool(d.get("popular", False)),
                )
            )
        except Exception:
            continue
    return plans if plans else [p for p in DEFAULT_PLANS]


@app.post("/lead")
def create_lead(lead: Lead):
    try:
        lead_id = create_document("lead", lead)
        return {"status": "ok", "id": lead_id}
    except Exception as e:
        # Even if DB unavailable, acknowledge capture for demo purposes
        return {"status": "ok", "id": None, "note": "Lead captured (no DB)", "error": str(e)[:120]}


@app.post("/subscribe")
def create_subscription(subscription: Subscription):
    try:
        sub_id = create_document("subscription", subscription)
        return {"status": "ok", "id": sub_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unable to create subscription: {str(e)[:200]}")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
