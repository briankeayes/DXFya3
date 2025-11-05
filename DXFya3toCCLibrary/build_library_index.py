#!/usr/bin/env python3
"""
Build an SQLite index of all Creative Cloud Libraries for fast lookups.
"""

import json
import os
import sqlite3
from pathlib import Path
from datetime import datetime

# Path to CC Libraries
BASE_PATH = Path.home() / "Library/Application Support/Adobe/Creative Cloud Libraries/LIBS/6D27744844570B5D992016E5_AdobeID"

# Database path
DB_PATH = Path(__file__).parent / "cc_libraries.db"

def create_database():
    """Create the SQLite database schema."""
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
    
    # Elements table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS elements (
            element_id TEXT PRIMARY KEY,
            library_id TEXT NOT NULL,
            element_name TEXT NOT NULL,
            element_type TEXT NOT NULL,
            element_path TEXT NOT NULL,
            file_type TEXT,
            file_name TEXT,
            file_size INTEGER,
            component_path TEXT,
            created_at INTEGER,
            modified_at INTEGER,
            FOREIGN KEY (library_id) REFERENCES libraries (library_id)
        )
    ''')
    
    # Create indexes for fast searches
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_library_name ON libraries(library_name)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_element_name ON elements(element_name)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_file_name ON elements(file_name)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_library_elements ON elements(library_id)')
    
    # Full-text search virtual table
    cursor.execute('''
        CREATE VIRTUAL TABLE IF NOT EXISTS elements_fts USING fts5(
            element_id UNINDEXED,
            element_name,
            file_name,
            library_name
        )
    ''')
    
    conn.commit()
    return conn

def get_component_path(library_path, components):
    """Extract the actual file path from components."""
    if not components:
        return None
    
    # Find primary component
    primary = None
    for comp in components:
        if comp.get('rel') == 'primary' and comp.get('path'):
            primary = comp
            break
    
    if not primary and components:
        primary = components[0]
    
    if not primary or 'path' not in primary:
        return None
    
    # Try the path from manifest first
    component_file = library_path / "components" / primary['path']
    if component_file.exists():
        return str(component_file)
    
    # If not found, search for AI files with similar naming
    components_dir = library_path / "components"
    if components_dir.exists():
        # Get file extension from primary
        file_type = primary.get('type', '')
        extension = '.ai' if 'illustrator' in file_type else ''
        
        # Search for any .ai files if this is an Illustrator component
        if extension:
            for ai_file in components_dir.glob(f"*{extension}"):
                # Return the first match (there's usually only one)
                return str(ai_file)
    
    return None

def index_library(conn, library_path, library_type):
    """Index a single library."""
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
                
                # Get file info from components
                components = element.get('components', [])
                file_type = None
                file_name = None
                file_size = 0
                component_path = get_component_path(library_path, components)
                
                if components:
                    primary = components[0]
                    file_type = primary.get('type', 'unknown')
                    if 'path' in primary:
                        file_name = element_name
                        if file_type == 'application/illustrator':
                            file_name = f"{element_name}.ai"
                    file_size = primary.get('length', 0)
                
                created = element.get('library#created')
                modified = element.get('library#modified')
                
                # Insert/update element
                cursor.execute('''
                    INSERT OR REPLACE INTO elements
                    (element_id, library_id, element_name, element_type, element_path,
                     file_type, file_name, file_size, component_path, created_at, modified_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (element_id, library_id, element_name, element_type, element_path,
                      file_type, file_name, file_size, component_path, created, modified))
                
                element_count += 1
    
    conn.commit()
    return element_count

def rebuild_fts(conn):
    """Rebuild the full-text search table from elements."""
    cursor = conn.cursor()
    
    # Clear the FTS table
    cursor.execute('DELETE FROM elements_fts')
    
    # Repopulate from elements table
    cursor.execute('''
        INSERT INTO elements_fts (element_id, element_name, file_name, library_name)
        SELECT e.element_id, e.element_name, e.file_name, l.library_name
        FROM elements e
        JOIN libraries l ON e.library_id = l.library_id
    ''')
    
    conn.commit()

def build_index():
    """Build the complete index of all libraries."""
    print("Building Creative Cloud Libraries index...")
    print(f"Database: {DB_PATH}")
    print()
    
    # Create database
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
                    # Get library name
                    manifest = library_dir / "manifest"
                    if manifest.exists():
                        try:
                            with open(manifest, 'r') as f:
                                data = json.load(f)
                                lib_name = data.get('name', 'Unknown')
                                print(f"  ✓ {lib_name}: {count} elements")
                        except:
                            print(f"  ✓ {library_dir.name}: {count} elements")
    
    # Index shared/collaborated libraries
    collab_path = BASE_PATH / "collaborated/dcx"
    if collab_path.exists():
        print("\nIndexing shared libraries...")
        for library_dir in collab_path.iterdir():
            if library_dir.is_dir():
                count = index_library(conn, library_dir, 'shared')
                if count > 0:
                    total_libraries += 1
                    total_elements += count
                    # Get library name
                    manifest = library_dir / "manifest"
                    if manifest.exists():
                        try:
                            with open(manifest, 'r') as f:
                                data = json.load(f)
                                lib_name = data.get('name', 'Unknown')
                                print(f"  ✓ {lib_name}: {count} elements")
                        except:
                            print(f"  ✓ {library_dir.name}: {count} elements")
    
    # Rebuild full-text search index (removes duplicates)
    print("\n🔄 Rebuilding search index...")
    rebuild_fts(conn)
    print("✅ Search index rebuilt")
    
    conn.close()
    
    print()
    print("=" * 60)
    print(f"✅ Index complete!")
    print(f"   Total libraries: {total_libraries}")
    print(f"   Total elements: {total_elements}")
    print(f"   Database: {DB_PATH}")
    print("=" * 60)

if __name__ == '__main__':
    build_index()

