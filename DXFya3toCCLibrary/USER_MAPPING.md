# User Name Mapping

## Problem Solved ✅

Adobe stores user IDs (like `B1551D8067296A4B0A495CC0@593b69a566462365495fbf.e`) instead of human names in the library metadata for privacy/security.

Now you can **map these IDs to real names**!

---

## Quick Start

### 1. Find All Users

```bash
python3 list_users.py
```

This shows all Adobe IDs found in your libraries and which ones need mapping.

### 2. Edit user_map.json

Open `user_map.json` and add names for the unmapped users:

```json
{
  "users": {
    "B1551D8067296A4B0A495CC0@593b69a566462365495fbf.e": {
      "name": "John Smith",
      "email": "john@example.com",
      "notes": "Lead designer"
    },
    "18D31E5266CC04BF0A495C94@AdobeID": {
      "name": "Jane Doe",
      "email": "jane@example.com",
      "notes": "Windows user"
    }
  }
}
```

### 3. View Files With Names

```bash
python3 show_metadata.py 02R
```

Now shows:
```
✏️  LAST MODIFIED BY
   User:         John Smith
   Device:       win-10.0.26100
```

Instead of:
```
✏️  LAST MODIFIED BY
   User:         B1551D8067296A4B0A495CC0@593b69a566462365495fbf.e
   Device:       win-10.0.26100
```

---

## Your Current Users

From your libraries, you have **5 users**:

1. **Brian (You)** - Your Adobe ID
   - 886 files created/modified
   - Main account

2. **User 1** - `B1551D8067296A4B0A495CC0...`
   - 236 files created
   - Uses Mac and Windows
   - **Modified 02R on Feb 5, 2025**

3. **User 2** - `18D31E5266CC04BF0A495C94...`
   - 116 files created
   - Windows user

4. **User 3** - `574871D8664623650A495E65...`
   - 128 files created, 239 modified
   - Active contributor

5. **UNMAPPED** - `0E7451005FF670190A495C19...`
   - 121 files created
   - ⚠️ Needs mapping!

---

## How to Identify Unknown Users

Ask your team:
1. "Who uses a Windows machine?" (check device info)
2. "Who recently edited file X?" (check timestamps)
3. Look at which files they created/modified
4. Check the device IDs - different devices = different hardware

Or just ask: "What's your Adobe ID?" and match it to the list.

---

## Files

- **`user_map.json`** - Your name mappings (edit this)
- **`list_users.py`** - Shows all Adobe IDs
- **`show_metadata.py`** - Now displays mapped names

---

## Tips

### Show Only Unmapped Users

```bash
python3 list_users.py | grep "UNMAPPED" -A 5
```

### Find Who Created a File

```bash
python3 show_metadata.py <filename> | grep "CREATED BY" -A 4
```

### Find Files by User

```bash
sqlite3 cc_libraries_enhanced.db \
  "SELECT element_name FROM elements \
   WHERE created_by_user = 'USER_ID_HERE' \
   LIMIT 10"
```

---

## Example: Answering "Who Last Edited 02R?"

**Before:**
```
✏️  LAST MODIFIED BY
   User:  B1551D8067296A4B0A495CC0@593b69a566462365495fbf.e
```
*"What? Who is that?"* 🤷

**After mapping:**
```
✏️  LAST MODIFIED BY
   User:  John Smith (john@example.com)
```
*"Ah, it was John!"* ✅

---

## Answer to Your Original Question

**Who last edited 02R?**

According to the metadata:
- **User:** User 1 (currently mapped name)
- **When:** February 5, 2025 at 2:03 PM
- **Device:** Windows 10 (win-10.0.26100)
- **Device ID:** bed6c485-ddc1-481f-b1f6-cd693080e8d5

To get the real name, edit `user_map.json` and replace "User 1" with the actual person's name!

---

**Last Updated:** November 2025  
**Files Tracked:** 1,493 elements  
**Users Found:** 5 unique Adobe IDs

