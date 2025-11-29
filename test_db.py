#!/usr/bin/env python3
import sqlite3
import sys
import os

try:
    # Test SQLite directly
    print("Testing SQLite database...")
    conn = sqlite3.connect('medical_scheduling.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print('Tables:', [t[0] for t in tables])
    
    cursor.execute('SELECT COUNT(*) FROM doctor_profiles;')
    doctors_count = cursor.fetchone()[0]
    print(f'Doctors count: {doctors_count}')
    
    cursor.execute('SELECT COUNT(*) FROM users;')
    users_count = cursor.fetchone()[0] 
    print(f'Users count: {users_count}')
    
    # Test a specific doctor
    cursor.execute('SELECT id, specialization, experience FROM doctor_profiles LIMIT 3;')
    doctors = cursor.fetchall()
    print('Sample doctors:', doctors)
    
    conn.close()
    print('✅ SQLite database access works fine')
    
    # Now test SQLAlchemy
    print("\nTesting SQLAlchemy...")
    sys.path.append('.')
    from backend.database.config import SessionLocal
    from backend.database.models import DoctorProfile, User
    
    db = SessionLocal()
    try:
        # Query through SQLAlchemy
        doctors = db.query(DoctorProfile).all()
        print(f'SQLAlchemy doctors count: {len(doctors)}')
        
        for doctor in doctors[:3]:
            print(f'  - {doctor.specialization}, Experience: {doctor.experience} years')
        
        print('✅ SQLAlchemy access works fine')
        
    except Exception as e:
        print(f'❌ SQLAlchemy error: {e}')
        import traceback
        traceback.print_exc()
    finally:
        db.close()
        
except Exception as e:
    print(f'❌ Database error: {e}')
    import traceback
    traceback.print_exc()