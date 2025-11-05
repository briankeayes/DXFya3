#!/usr/bin/env python3
"""
Display full metadata for Creative Cloud Library elements.
"""

import sqlite3
import sys
import json
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "cc_libraries_enhanced.db"
USER_MAP_PATH = Path(__file__).parent / "user_map.json"

def load_user_map():
    """Load user ID to name mapping."""
    if not USER_MAP_PATH.exists():
        return {}
    try:
        with open(USER_MAP_PATH) as f:
            data = json.load(f)
            return data.get('users', {})
    except:
        return {}

def get_user_name(user_id):
    """Get human-readable name for a user ID."""
    if not user_id:
        return "N/A"
    
    user_map = load_user_map()
    
    if user_id in user_map:
        user_info = user_map[user_id]
        name = user_info.get('name', user_id)
        email = user_info.get('email', '')
        if email:
            return f"{name} ({email})"
        return name
    
    # Return shortened ID if no mapping
    short_id = user_id.split('@')[0]
    return f"{short_id}... (unknown - add to user_map.json)"

def timestamp_to_date(ts):
    """Convert millisecond timestamp to readable date."""
    if not ts:
        return "N/A"
    try:
        return datetime.fromtimestamp(ts / 1000).strftime('%Y-%m-%d %H:%M:%S')
    except:
        return "N/A"

def show_element_metadata(element_name, library_name=None):
    """Display full metadata for an element."""
    if not DB_PATH.exists():
        print("❌ Enhanced database not found. Run build_library_index_enhanced.py first.")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get element with full metadata
    if library_name:
        cursor.execute('''
            SELECT e.*, l.library_name, l.library_type
            FROM elements e
            JOIN libraries l ON e.library_id = l.library_id
            WHERE e.element_name = ? AND l.library_name = ?
        ''', (element_name, library_name))
    else:
        cursor.execute('''
            SELECT e.*, l.library_name, l.library_type
            FROM elements e
            JOIN libraries l ON e.library_id = l.library_id
            WHERE e.element_name = ?
            ORDER BY e.modified_at DESC
        ''', (element_name,))
    
    result = cursor.fetchone()
    
    if not result:
        print(f"❌ Element not found: {element_name}")
        conn.close()
        return
    
    # Map column names
    columns = [desc[0] for desc in cursor.description]
    elem = dict(zip(columns, result))
    
    # Get version history
    cursor.execute('''
        SELECT * FROM version_history
        WHERE element_id = ?
        ORDER BY version_number DESC
    ''', (elem['element_id'],))
    
    versions = cursor.fetchall()
    version_cols = [desc[0] for desc in cursor.description]
    
    conn.close()
    
    # Display metadata
    print()
    print("=" * 80)
    print(f"📄 {elem['element_name']}")
    print("=" * 80)
    
    print(f"\n🏷️  BASIC INFO")
    print(f"   Library:      {elem['library_name']} ({elem['library_type']})")
    print(f"   Element Type: {elem['element_type']}")
    print(f"   File Name:    {elem['file_name']}")
    print(f"   File Type:    {elem['file_type']}")
    print(f"   File Size:    {elem['file_size']:,} bytes" if elem['file_size'] else "   File Size:    N/A")
    print(f"   Element ID:   {elem['element_id']}")
    
    print(f"\n📅 TIMESTAMPS")
    print(f"   Created:      {timestamp_to_date(elem['created_at'])}")
    print(f"   Modified:     {timestamp_to_date(elem['modified_at'])}")
    
    print(f"\n👤 CREATED BY")
    print(f"   User:         {get_user_name(elem['created_by_user'])}")
    print(f"   Device:       {elem['created_by_device'] or 'N/A'}")
    print(f"   Device ID:    {elem['created_by_device_id'] or 'N/A'}")
    print(f"   App:          {elem['created_by_app'] or 'N/A'}")
    
    print(f"\n✏️  LAST MODIFIED BY")
    print(f"   User:         {get_user_name(elem['modified_by_user'])}")
    print(f"   Device:       {elem['modified_by_device'] or 'N/A'}")
    print(f"   Device ID:    {elem['modified_by_device_id'] or 'N/A'}")
    print(f"   App:          {elem['modified_by_app'] or 'N/A'}")
    
    print(f"\n🔐 COMPONENT/FILE INFO")
    print(f"   Component ID: {elem['component_id'] or 'N/A'}")
    print(f"   SHA256:       {elem['component_sha256'] or 'N/A'}")
    print(f"   MD5:          {elem['component_md5'] or 'N/A'}")
    print(f"   ETag:         {elem['component_etag'] or 'N/A'}")
    print(f"   Version:      {elem['component_version'] or 'N/A'}")
    print(f"   State:        {elem['component_state'] or 'N/A'}")
    print(f"   Full Size:    {'Yes' if elem['component_is_full_size'] else 'No'}")
    
    print(f"\n🔗 CREATIVE CLOUD")
    print(f"   Asset ID:     {elem['asset_id'] or 'N/A'}")
    print(f"   Latest Ver:   {elem['latest_version'] or 'N/A'}")
    
    if elem['groups']:
        try:
            groups_data = json.loads(elem['groups'])
            print(f"\n📁 GROUPS")
            for group_id, group_info in groups_data.items():
                print(f"   {group_id}: {group_info}")
        except:
            pass
    
    if elem['component_path']:
        print(f"\n💾 LOCAL FILE PATH")
        print(f"   {elem['component_path']}")
    
    if versions:
        print(f"\n📜 VERSION HISTORY ({elem['version_count']} versions)")
        print(f"   {'Ver':<5} {'Modified':<20} {'Modified By':<40} {'Asset Version':<15}")
        print(f"   {'-'*5} {'-'*20} {'-'*40} {'-'*15}")
        for version in versions[:10]:  # Show last 10 versions
            ver_dict = dict(zip(version_cols, version))
            ver_num = ver_dict['version_number']
            mod_time = timestamp_to_date(ver_dict['modified_at'])
            mod_by = ver_dict['modified_by']
            asset_ver = ver_dict['asset_version'] or 'N/A'
            # Get human-readable name
            mod_by_name = get_user_name(mod_by)
            # Truncate for display if needed
            if len(mod_by_name) > 40:
                mod_by_name = mod_by_name[:37] + "..."
            print(f"   {ver_num:<5} {mod_time:<20} {mod_by_name:<40} {asset_ver:<15}")
        
        if len(versions) > 10:
            print(f"   ... and {len(versions) - 10} more versions")
    
    print()
    print("=" * 80)
    print()

def main():
    """Command-line interface."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 show_metadata.py <element_name> [<library_name>]")
        print()
        print("Examples:")
        print("  python3 show_metadata.py RT007760")
        print("  python3 show_metadata.py RT007760-bkdxfya librarytest")
        print("  python3 show_metadata.py RT007801 \"RaD Mechanical Design Library\"")
        return
    
    element_name = sys.argv[1]
    library_name = sys.argv[2] if len(sys.argv) > 2 else None
    
    show_element_metadata(element_name, library_name)

if __name__ == '__main__':
    main()

