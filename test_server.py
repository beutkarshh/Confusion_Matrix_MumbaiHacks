#!/usr/bin/env python3
"""
Minimal server test to identify the issue
"""

import sys
import os
from fastapi import FastAPI

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

app = FastAPI(title="Test API")

@app.get("/")
def root():
    return {"message": "Test server is running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

# Test database connection
@app.get("/test-db")
def test_database():
    try:
        from backend.database.config import SessionLocal
        from backend.database.models import DoctorProfile, User
        
        db = SessionLocal()
        try:
            doctors = db.query(DoctorProfile).count()
            users = db.query(User).count()
            return {"doctors": doctors, "users": users, "status": "database_ok"}
        finally:
            db.close()
    except Exception as e:
        return {"error": str(e), "status": "database_error"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)