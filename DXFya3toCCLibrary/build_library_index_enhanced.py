#!/usr/bin/env python3
"""
Build an enhanced SQLite index with full metadata from Creative Cloud Libraries.
"""

import json
import os
import sqlite3
from pathlib import Path
from datetime import datetime

# Path to CC Libraries
BASE_PATH = Path.home() / "Library/Application Support/Adobe/Creative Cloud Libraries/LIBS/6D27744844570B5D992016E5_AdobeID"

# Database path
DB_PATH = Path(__file__).parent / "cc_libraries_enhanced.db"

def create_database():
    """Create the enhanced SQLite database schema."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Libraries table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS libraries (
            library_id TEXT PRIMARY KEY,
            library_name TEXT NOT NULL,
            library_type TEXT NOT NULL,
            library_path TEXT NOT NULL,
            created_at INTEGER,
            modified_at INTEGER,
            indexed_at INTEGER NOT NULL
        )
    ''')
    
    # Enhanced elements table with full metadata
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS elements (
            element_id TEXT PRIMARY KEY,
            library_id TEXT NOT NULL,
            element_name TEXT NOT NULL,
            element_type TEXT NOT NULL,
            element_path TEXT NOT NULL,
            
            -- File info
            file_type TEXT,
            file_name TEXT,
            file_size INTEGER,
            component_path TEXT,
            
            -- Timestamps
            created_at INTEGER,
            modified_at INTEGER,
            
            -- Created by metadata
            created_by_user TEXT,
            created_by_device TEXT,
            created_by_device_id TEXT,
            created_by_app TEXT,
            
            -- Modified by metadata
            modified_by_user TEXT,
            modified_by_device TEXT,
            modified_by_device_id TEXT,
            modified_by_app TEXT,
            
            -- Component metadata
            component_id TEXT,
            component_sha256 TEXT,
            component_md5 TEXT,
            component_etag TEXT,
            component_version TEXT,
            component_state TEXT,
            component_is_full_size INTEGER,
            
            -- History & versioning
            version_count INTEGER,
            asset_id TEXT,
            latest_version TEXT,
            
            -- Groups/organization
            groups TEXT,
            
            FOREIGN KEY (library_id) REFERENCES libraries (library_id)
        )
    ''')
    
    # Version history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS version_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            element_id TEXT NOT NULL,
            version_number INTEGER,
            modified_at INTEGER,
            modified_by TEXT,
            thumbnail_component_id TEXT,
            asset_id TEXT,
            asset_version TEXT,
            FOREIGN KEY (element_id) REFERENCES elements (element_id)
        )
    ''')
    
    # Create indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_library_name ON libraries(library_name)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_element_name ON elements(element_name)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_file_name ON elements(file_name)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_library_elements ON elements(library_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_created_by ON elements(created_by_user)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_modified_by ON elements(modified_by_user)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_version_element ON version_history(element_id)')
    
    # Full-text search
    cursor.execute('''
        CREATE VIRTUAL TABLE IF NOT EXISTS elements_fts USING fts5(
            element_id UNINDEXED,
            element_name,
            file_name,
            library_name,
            created_by_user,
            modified_by_user
        )
    ''')
    
    conn.commit()
    return conn

def get_component_path(library_path, components):
    """Extract the actual file path from components."""
    if not components:
        return None, None
    
    # Find primary component
    primary = None
    for comp in components:
        if comp.get('rel') == 'primary':
            primary = comp
            break
    
    if not primary and components:
        primary = components[0]
    
    if not primary:
        return None, None
    
    # Get component info
    component_info = {
        'id': primary.get('id'),
        'sha256': primary.get('library#sha256'),
        'md5': primary.get('md5'),
        'etag': primary.get('etag'),
        'version': primary.get('version'),
        'state': primary.get('state'),
        'is_full_size': 1 if primary.get('library#isFullSize') else 0
    }
    
    # Try to find the file
    if 'path' not in primary:
        return None, component_info
    
    component_file = library_path / "components" / primary['path']
    if component_file.exists():
        return str(component_file), component_info
    
    # Fallback: search for AI files
    components_dir = library_path / "components"
    if components_dir.exists():
        file_type = primary.get('type', '')
        extension = '.ai' if 'illustrator' in file_type else ''
        if extension:
            for ai_file in components_dir.glob(f"*{extension}"):
                return str(ai_file), component_info
    
    return None, component_info

def index_library(conn, library_path, library_type):
    """Index a single library with enhanced metadata."""
    manifest_file = library_path / "manifest"
    
    if not manifest_file.exists():
        return 0
    
    try:
        with open(manifest_file, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        return 0
    
    library_id = data.get('id')
    library_name = data.get('name', 'Untitled')
    created = data.get('library#created')
    modified = data.get('library#modified')
    
    cursor = conn.cursor()
    
    # Insert/update library
    cursor.execute('''
        INSERT OR REPLACE INTO libraries 
        (library_id, library_name, library_type, library_path, created_at, modified_at, indexed_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (library_id, library_name, library_type, str(library_path), 
          created, modified, int(datetime.now().timestamp() * 1000)))
    
    # Process elements
    element_count = 0
    children = data.get('children', [])
    
    for child in children:
        if child.get('name') == 'elements':
            for element in child.get('children', []):
                element_id = element.get('id')
                element_name = element.get('name', 'Untitled')
                element_type = element.get('type', '')
                element_path = element.get('path', '')
                
                # Get timestamps
                created_at = element.get('library#created')
                modified_at = element.get('library#modified')
                
                # Extract created by metadata
                created_data = element.get('library#createdData', {})
                created_by_user = created_data.get('userId')
                created_by_device = created_data.get('device')
                created_by_device_id = created_data.get('deviceId')
                created_by_app = created_data.get('app')
                
                # Extract modified by metadata
                modified_data = element.get('library#modifiedData', {})
                modified_by_user = modified_data.get('userId')
                modified_by_device = modified_data.get('device')
                modified_by_device_id = modified_data.get('deviceId')
                modified_by_app = modified_data.get('app')
                
                # Get component info
                components = element.get('components', [])
                component_path, component_info = get_component_path(library_path, components)
                
                # File info
                file_type = None
                file_name = None
                file_size = 0
                
                if components:
                    primary = components[0]
                    file_type = primary.get('type', 'unknown')
                    if 'path' in primary:
                        file_name = element_name
                        if file_type == 'application/illustrator':
                            file_name = f"{element_name}.ai"
                    file_size = primary.get('length', 0)
                
                # Version history
                history = element.get('library#history', [])
                version_count = len(history)
                asset_id = None
                latest_version = None
                
                if history:
                    latest = history[0]
                    ref = latest.get('reference', {})
                    asset_id = ref.get('repo:assetId')
                    latest_version = ref.get('repo:version')
                
                # Groups
                groups = json.dumps(element.get('library#groups', {})) if element.get('library#groups') else None
                
                # Insert/update element with full metadata
                cursor.execute('''
                    INSERT OR REPLACE INTO elements
                    (element_id, library_id, element_name, element_type, element_path,
                     file_type, file_name, file_size, component_path,
                     created_at, modified_at,
                     created_by_user, created_by_device, created_by_device_id, created_by_app,
                     modified_by_user, modified_by_device, modified_by_device_id, modified_by_app,
                     component_id, component_sha256, component_md5, component_etag,
                     component_version, component_state, component_is_full_size,
                     version_count, asset_id, latest_version, groups)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (element_id, library_id, element_name, element_type, element_path,
                      file_type, file_name, file_size, component_path,
                      created_at, modified_at,
                      created_by_user, created_by_device, created_by_device_id, created_by_app,
                      modified_by_user, modified_by_device, modified_by_device_id, modified_by_app,
                      component_info['id'] if component_info else None,
                      component_info['sha256'] if component_info else None,
                      component_info['md5'] if component_info else None,
                      component_info['etag'] if component_info else None,
                      component_info['version'] if component_info else None,
                      component_info['state'] if component_info else None,
                      component_info['is_full_size'] if component_info else 0,
                      version_count, asset_id, latest_version, groups))
                
                # Insert version history
                cursor.execute('DELETE FROM version_history WHERE element_id = ?', (element_id,))
                for idx, hist in enumerate(history):
                    ref = hist.get('reference', {})
                    cursor.execute('''
                        INSERT INTO version_history
                        (element_id, version_number, modified_at, modified_by,
                         thumbnail_component_id, asset_id, asset_version)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (element_id, idx + 1, hist.get('modified'),
                          hist.get('modifiedBy'), hist.get('thumbnailComponentId'),
                          ref.get('repo:assetId'), ref.get('repo:version')))
                
                element_count += 1
    
    conn.commit()
    return element_count

def rebuild_fts(conn):
    """Rebuild the full-text search table."""
    cursor = conn.cursor()
    cursor.execute('DELETE FROM elements_fts')
    cursor.execute('''
        INSERT INTO elements_fts 
        (element_id, element_name, file_name, library_name, created_by_user, modified_by_user)
        SELECT e.element_id, e.element_name, e.file_name, l.library_name,
               e.created_by_user, e.modified_by_user
        FROM elements e
        JOIN libraries l ON e.library_id = l.library_id
    ''')
    conn.commit()

def build_index():
    """Build the enhanced index."""
    print("Building Enhanced Creative Cloud Libraries Index")
    print("=" * 60)
    print(f"Database: {DB_PATH}")
    print()
    
    conn = create_database()
    
    total_libraries = 0
    total_elements = 0
    
    # Index private libraries
    private_path = BASE_PATH / "creative_cloud/dcx"
    if private_path.exists():
        print("Indexing private libraries...")
        for library_dir in private_path.iterdir():
            if library_dir.is_dir():
                count = index_library(conn, library_dir, 'private')
                if count > 0:
                    total_libraries += 1
                    total_elements += count
                    manifest = library_dir / "manifest"
                    if manifest.exists():
                        try:
                            with open(manifest, 'r') as f:
                                data = json.load(f)
                                lib_name = data.get('name', 'Unknown')
                                print(f"  ✓ {lib_name}: {count} elements")
                        except:
                            print(f"  ✓ {library_dir.name}: {count} elements")
    
    # Index shared libraries
    collab_path = BASE_PATH / "collaborated/dcx"
    if collab_path.exists():
        print("\nIndexing shared libraries...")
        for library_dir in collab_path.iterdir():
            if library_dir.is_dir():
                count = index_library(conn, library_dir, 'shared')
                if count > 0:
                    total_libraries += 1
                    total_elements += count
                    manifest = library_dir / "manifest"
                    if manifest.exists():
                        try:
                            with open(manifest, 'r') as f:
                                data = json.load(f)
                                lib_name = data.get('name', 'Unknown')
                                print(f"  ✓ {lib_name}: {count} elements")
                        except:
                            print(f"  ✓ {library_dir.name}: {count} elements")
    
    # Rebuild FTS
    print("\n🔄 Rebuilding search index...")
    rebuild_fts(conn)
    print("✅ Search index rebuilt")
    
    conn.close()
    
    print()
    print("=" * 60)
    print(f"✅ Enhanced index complete!")
    print(f"   Total libraries: {total_libraries}")
    print(f"   Total elements: {total_elements}")
    print(f"   Database: {DB_PATH}")
    print()
    print("📊 Enhanced metadata captured:")
    print("   • Created by (user, device, app)")
    print("   • Modified by (user, device, app)")
    print("   • Component hashes (SHA256, MD5)")
    print("   • Version history (full change log)")
    print("   • Asset references (Creative Cloud)")
    print("=" * 60)

if __name__ == '__main__':
    build_index()

