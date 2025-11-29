#!/usr/bin/env python3
"""
Fix user roles to match enum values
"""
import sqlite3

def fix_user_roles():
    conn = sqlite3.connect('medical_scheduling.db')
    cursor = conn.cursor()
    
    # Update roles to match enum values
    cursor.execute("UPDATE users SET role = 'PATIENT' WHERE role = 'patient'")
    cursor.execute("UPDATE users SET role = 'DOCTOR' WHERE role = 'doctor'")
    conn.commit()
    
    print('✅ Reverted user roles to uppercase')
    
    # Verify the update
    cursor.execute('SELECT id, name, role FROM users;')
    users = cursor.fetchall()
    print('\nUpdated user roles:')
    for user in users:
        print(f'  ID: {user[0]}, Name: {user[1]}, Role: {user[2]}')
    
    conn.close()

if __name__ == "__main__":
    fix_user_roles()