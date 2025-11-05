#!/usr/bin/env python3
"""
Search Creative Cloud Libraries using the indexed database.
"""

import sqlite3
import sys
import json
from pathlib import Path

DB_PATH = Path(__file__).parent / "cc_libraries.db"

def search_elements(query, library_name=None, limit=50):
    """Search for elements by name or file name."""
    if not DB_PATH.exists():
        print("❌ Database not found. Run build_library_index.py first.")
        return []
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if library_name:
        # Search within specific library
        cursor.execute('''
            SELECT e.element_id, e.element_name, e.file_name, e.file_type, 
                   e.component_path, l.library_name, l.library_type
            FROM elements e
            JOIN libraries l ON e.library_id = l.library_id
            WHERE (e.element_name LIKE ? OR e.file_name LIKE ?)
              AND l.library_name LIKE ?
            ORDER BY e.element_name
            LIMIT ?
        ''', (f'%{query}%', f'%{query}%', f'%{library_name}%', limit))
    else:
        # Search all libraries using full-text search
        cursor.execute('''
            SELECT e.element_id, e.element_name, e.file_name, e.file_type,
                   e.component_path, l.library_name, l.library_type
            FROM elements_fts fts
            JOIN elements e ON fts.element_id = e.element_id
            JOIN libraries l ON e.library_id = l.library_id
            WHERE elements_fts MATCH ?
            ORDER BY rank
            LIMIT ?
        ''', (query, limit))
    
    results = cursor.fetchall()
    conn.close()
    
    return results

def get_element_by_name(element_name, library_name=None):
    """Get exact element match."""
    if not DB_PATH.exists():
        print("❌ Database not found. Run build_library_index.py first.")
        return None
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if library_name:
        cursor.execute('''
            SELECT e.element_id, e.element_name, e.file_name, e.file_type,
                   e.component_path, e.file_size, l.library_name, l.library_type,
                   l.library_path, e.element_path
            FROM elements e
            JOIN libraries l ON e.library_id = l.library_id
            WHERE e.element_name = ? AND l.library_name = ?
        ''', (element_name, library_name))
    else:
        cursor.execute('''
            SELECT e.element_id, e.element_name, e.file_name, e.file_type,
                   e.component_path, e.file_size, l.library_name, l.library_type,
                   l.library_path, e.element_path
            FROM elements e
            JOIN libraries l ON e.library_id = l.library_id
            WHERE e.element_name = ?
            ORDER BY e.modified_at DESC
        ''', (element_name,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            'element_id': result[0],
            'element_name': result[1],
            'file_name': result[2],
            'file_type': result[3],
            'component_path': result[4],
            'file_size': result[5],
            'library_name': result[6],
            'library_type': result[7],
            'library_path': result[8],
            'element_path': result[9]
        }
    return None

def list_libraries():
    """List all indexed libraries."""
    if not DB_PATH.exists():
        print("❌ Database not found. Run build_library_index.py first.")
        return []
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT l.library_id, l.library_name, l.library_type, COUNT(e.element_id)
        FROM libraries l
        LEFT JOIN elements e ON l.library_id = e.library_id
        GROUP BY l.library_id
        ORDER BY l.library_name
    ''')
    
    results = cursor.fetchall()
    conn.close()
    
    return results

def main():
    """Command-line interface."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 search_libraries.py list                    # List all libraries")
        print("  python3 search_libraries.py search <query>          # Search all libraries")
        print("  python3 search_libraries.py search <query> <library> # Search specific library")
        print("  python3 search_libraries.py get <name> [<library>]  # Get exact match")
        print()
        print("Examples:")
        print("  python3 search_libraries.py search RT007760")
        print("  python3 search_libraries.py search RT007760 librarytest")
        print("  python3 search_libraries.py get RT007760-bkdxfya librarytest")
        return
    
    command = sys.argv[1]
    
    if command == 'list':
        libraries = list_libraries()
        print("\n📚 Creative Cloud Libraries\n")
        print(f"{'Library Name':<40} {'Type':<10} {'Elements':<10}")
        print("=" * 62)
        for lib_id, lib_name, lib_type, count in libraries:
            print(f"{lib_name:<40} {lib_type:<10} {count:<10}")
        print()
    
    elif command == 'search':
        if len(sys.argv) < 3:
            print("❌ Please provide a search query")
            return
        
        query = sys.argv[2]
        library = sys.argv[3] if len(sys.argv) > 3 else None
        
        results = search_elements(query, library)
        
        if not results:
            print(f"❌ No results found for: {query}")
            return
        
        print(f"\n🔍 Search results for: {query}\n")
        print(f"{'Element Name':<30} {'Library':<25} {'Type':<15}")
        print("=" * 72)
        
        for elem_id, elem_name, file_name, file_type, comp_path, lib_name, lib_type in results:
            file_indicator = "📄" if comp_path else "  "
            print(f"{file_indicator} {elem_name:<28} {lib_name:<25} {lib_type:<15}")
        
        print(f"\nFound {len(results)} results")
        print()
    
    elif command == 'get':
        if len(sys.argv) < 3:
            print("❌ Please provide an element name")
            return
        
        element_name = sys.argv[2]
        library = sys.argv[3] if len(sys.argv) > 3 else None
        
        result = get_element_by_name(element_name, library)
        
        if not result:
            print(f"❌ Element not found: {element_name}")
            return
        
        print("\n📄 Element Details\n")
        print(f"  Element Name: {result['element_name']}")
        print(f"  File Name:    {result['file_name']}")
        print(f"  Library:      {result['library_name']} ({result['library_type']})")
        print(f"  File Type:    {result['file_type']}")
        print(f"  File Size:    {result['file_size']:,} bytes")
        print(f"  Element ID:   {result['element_id']}")
        
        if result['component_path']:
            print(f"\n  📁 File Path:")
            print(f"     {result['component_path']}")
        
        print()
        
        # Output as JSON for programmatic use
        if '--json' in sys.argv:
            print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()

