#!/usr/bin/env python3
"""
List all unique Adobe IDs found in your libraries.
Use this to populate user_map.json with real names.
"""

import sqlite3
import json
from pathlib import Path

DB_PATH = Path(__file__).parent / "cc_libraries_enhanced.db"
USER_MAP_PATH = Path(__file__).parent / "user_map.json"

def list_all_users():
    """List all unique user IDs and their activity."""
    if not DB_PATH.exists():
        print("❌ Enhanced database not found. Run build_library_index_enhanced.py first.")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get all unique creators
    cursor.execute('''
        SELECT 
            created_by_user,
            COUNT(*) as files_created,
            MIN(created_at) as first_seen,
            MAX(created_at) as last_seen
        FROM elements
        WHERE created_by_user IS NOT NULL
        GROUP BY created_by_user
    ''')
    
    creators = cursor.fetchall()
    
    # Get all unique modifiers
    cursor.execute('''
        SELECT 
            modified_by_user,
            COUNT(*) as files_modified,
            MIN(modified_at) as first_modified,
            MAX(modified_at) as last_modified
        FROM elements
        WHERE modified_by_user IS NOT NULL
        GROUP BY modified_by_user
    ''')
    
    modifiers = cursor.fetchall()
    
    conn.close()
    
    # Load existing user map
    user_map = {}
    if USER_MAP_PATH.exists():
        try:
            with open(USER_MAP_PATH) as f:
                data = json.load(f)
                user_map = data.get('users', {})
        except:
            pass
    
    # Combine all users
    all_users = {}
    
    for user_id, count, first, last in creators:
        if user_id not in all_users:
            all_users[user_id] = {
                'created': count,
                'modified': 0,
                'first_seen': first,
                'last_seen': last
            }
    
    for user_id, count, first, last in modifiers:
        if user_id in all_users:
            all_users[user_id]['modified'] = count
            all_users[user_id]['last_seen'] = max(all_users[user_id]['last_seen'], last)
        else:
            all_users[user_id] = {
                'created': 0,
                'modified': count,
                'first_seen': first,
                'last_seen': last
            }
    
    # Display results
    print("\n" + "=" * 80)
    print("👥 ADOBE IDS FOUND IN YOUR LIBRARIES")
    print("=" * 80)
    print()
    
    for idx, (user_id, stats) in enumerate(sorted(all_users.items()), 1):
        mapped_name = user_map.get(user_id, {}).get('name', '❓ UNMAPPED')
        
        print(f"{idx}. Adobe ID: {user_id}")
        print(f"   Current Name: {mapped_name}")
        print(f"   Files Created: {stats['created']}")
        print(f"   Files Modified: {stats['modified']}")
        print(f"   First Seen: {stats['first_seen']}")
        print(f"   Last Seen: {stats['last_seen']}")
        
        if mapped_name == '❓ UNMAPPED':
            print(f"   ⚠️  Add this to user_map.json!")
        
        print()
    
    print("=" * 80)
    print(f"\nTotal unique users: {len(all_users)}")
    print(f"Mapped users: {sum(1 for u in all_users if u in user_map)}")
    print(f"Unmapped users: {sum(1 for u in all_users if u not in user_map)}")
    print()
    print("💡 Edit user_map.json to add real names for unmapped users")
    print("=" * 80)
    print()

if __name__ == '__main__':
    list_all_users()

