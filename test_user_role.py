#!/usr/bin/env python3
"""
Test the authentication and role checking for booking
"""
import sys
sys.path.append('.')

from backend.database.config import SessionLocal
from backend.database.models import User, UserRole

def test_user_role():
    db = SessionLocal()
    try:
        # Test user Alice Johnson (ID 5)
        user = db.query(User).filter(User.id == 5).first()
        if user:
            print(f"User: {user.name}")
            print(f"Role from DB: {user.role}")
            print(f"Role type: {type(user.role)}")
            print(f"UserRole.PATIENT: {UserRole.PATIENT}")
            print(f"UserRole.PATIENT type: {type(UserRole.PATIENT)}")
            print(f"Comparison result: {user.role == UserRole.PATIENT}")
            print(f"Role value: {user.role.value if hasattr(user.role, 'value') else 'no value attr'}")
        else:
            print("User not found")
    finally:
        db.close()

if __name__ == "__main__":
    test_user_role()