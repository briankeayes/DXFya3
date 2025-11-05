# Creative Cloud Library Index System

**⚡ Lightning-fast access to your Creative Cloud Libraries**

Instead of parsing JSON manifests every time (which takes minutes), this system builds a SQLite database index for instant lookups.

## The Problem It Solves

**Before:** Opening a file from Creative Cloud Libraries required:
- Searching through directory structures with UUIDs
- Parsing multiple JSON manifest files
- Mapping library names → library IDs → element IDs → component paths
- **Time: 2-5 minutes** ⏱️

**After:** With the indexed database:
- Instant SQL query
- Direct file path retrieval
- **Time: 0.03 seconds** ⚡

## Quick Start

### 1. Build the Index (first time only)

```bash
cd ~/Dropbox/dev/Raider-new/DXFya3toCCLibrary
./cclib update
```

This indexes all your Creative Cloud Libraries (~1,500 elements in ~2 seconds).

### 2. Search Your Libraries

```bash
# Search all libraries
./cclib search RT007760

# Search within specific library
./cclib search RT007760 librarytest
```

### 3. Open Files Instantly

```bash
# Open in Illustrator (finds the file and opens it)
./cclib open RT007760-bkdxfya librarytest

# Or from any library (uses most recent if multiple matches)
./cclib open RT007760
```

### 4. Get Detailed Info

```bash
./cclib get RT007760-bkdxfya librarytest
```

Output:
```
📄 Element Details

  Element Name: RT007760-bkdxfya
  File Name:    RT007760-bkdxfya.ai
  Library:      librarytest (private)
  File Type:    application/illustrator
  File Size:    379,485 bytes
  Element ID:   9c2da393-b74c-44a0-a28f-6c1dfe06aa79

  📁 File Path:
     /Users/.../components/620fd10d-5f3b-4927-a0d9-e7c1642ece1d.ai
```

### 5. List All Libraries

```bash
./cclib list
```

## Database Structure

The system creates `cc_libraries.db` with three tables:

### Libraries Table
- `library_id` - UUID from Adobe
- `library_name` - Human-readable name
- `library_type` - 'private' or 'shared'
- `library_path` - Local cache path
- Timestamps

### Elements Table
- `element_id` - UUID for the element
- `library_id` - Foreign key to libraries
- `element_name` - Display name
- `element_type` - MIME type
- `file_name` - Actual filename
- `component_path` - **Direct path to cached file**
- Metadata (size, type, etc.)

### Full-Text Search (FTS5)
- Fast fuzzy searching across element names, file names, and library names

## Updating the Index

Run this whenever you add new files to your libraries:

```bash
./cclib update
```

**Note:** The update is fast (~2 seconds) and can be automated with a cron job if desired.

## Advanced Usage

### Python API

You can import the modules directly:

```python
from search_libraries import get_element_by_name, search_elements

# Get exact element
element = get_element_by_name("RT007760-bkdxfya", "librarytest")
print(element['component_path'])

# Search
results = search_elements("RT007", limit=10)
for result in results:
    print(result)
```

### JSON Output

```bash
./cclib get RT007760-bkdxfya librarytest --json
```

## Files in This System

- **`cclib`** - Main command-line wrapper
- **`build_library_index.py`** - Builds/updates the database
- **`search_libraries.py`** - Search and query functions
- **`open_from_library.py`** - Opens files in Illustrator
- **`cc_libraries.db`** - SQLite database (auto-generated)

## Performance Comparison

| Operation | Before | After | Improvement |
|-----------|--------|-------|-------------|
| Find file in library | 2-5 min | 0.03 sec | **4,000x faster** |
| Search all libraries | N/A | 0.05 sec | Instant |
| Open file | 3-5 min | 2 sec | **90x faster** |

## Maintenance

### When to Update the Index

- After adding new files to libraries
- After creating new libraries
- Periodically (once a day if actively using libraries)

### Automatic Updates

Add to crontab for daily updates:

```bash
crontab -e
```

Add:
```
0 9 * * * cd ~/Dropbox/dev/Raider-new/DXFya3toCCLibrary && ./cclib update >> /tmp/cclib_update.log 2>&1
```

## Troubleshooting

### "Database not found"
Run `./cclib update` to build the initial index.

### "File not found on disk"
The file hasn't synced from Creative Cloud yet. Check your Creative Cloud app sync status.

### "Element not found"
- Check spelling
- Run `./cclib update` to refresh the index
- Use `./cclib search <partial_name>` to find similar names

## How It Works

1. **Indexing Phase** (run once):
   - Scans `~/Library/Application Support/Adobe/Creative Cloud Libraries/`
   - Parses all `manifest` files (JSON)
   - Extracts library names, element names, and component paths
   - Stores in SQLite with indexes on searchable fields

2. **Search Phase** (instant):
   - SQL query against indexed database
   - Full-text search for fuzzy matching
   - Returns results in milliseconds

3. **Open Phase** (2 seconds):
   - Database lookup (0.03s)
   - Check file exists locally
   - AppleScript to open in Illustrator (2s)

## Integration with Illustrator MCP

You can use this with the Illustrator MCP:

```python
from search_libraries import get_element_by_name

# Get file path
element = get_element_by_name("RT007760-bkdxfya", "librarytest")

if element and element['component_path']:
    # Use MCP to open in Illustrator
    mcp_illustrator_run(f'''
        var file = new File("{element['component_path']}");
        app.open(file);
    ''')
```

---

**Built:** November 2025  
**Database:** SQLite 3 with FTS5 full-text search  
**Indexed:** 7 libraries, 1,493 elements  
**Average Query Time:** 31ms

