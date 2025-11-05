# Quick Start Guide

## ⚡ Instant Library Access

### 🌐 NEW: Web Interface (Easiest!)

```bash
cd ~/Dropbox/dev/Raider-new/DXFya3toCCLibrary
./start_search_ui.sh
```
Then open: **http://localhost:5001**

Beautiful search interface with filters, stats, and detailed views!

### 💻 Command Line (Fast!)

```bash
cd ~/Dropbox/dev/Raider-new/DXFya3toCCLibrary
./cclib open <filename> <library>
```

### Examples:

```bash
# Open RT007760-bkdxfya from librarytest (5 seconds total)
./cclib open RT007760-bkdxfya librarytest

# Search for files
./cclib search RT007760

# List all libraries
./cclib list

# Update index after adding new files
./cclib update
```

## Performance

| Task | Before | After |
|------|--------|-------|
| Find file | 2-5 min | **0.03 sec** |
| Open file | 3-5 min | **5 sec** |

## Why So Fast?

**Before:** Had to parse JSON manifests and traverse UUIDs every time  
**After:** Pre-indexed SQLite database with instant lookups

## Setup (Already Done!)

✅ Database built: `cc_libraries.db`  
✅ 7 libraries indexed  
✅ 1,493 elements indexed  
✅ Scripts ready to use

## Maintenance

Run this once a day or after adding files:
```bash
./cclib update
```

---

**See README_CCLIB.md for full documentation**

