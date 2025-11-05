# Changelog

## Version 3.1 - Fully Automated (No User Interaction) + Creative Cloud Integration

### Major Changes
- **Eliminated all user interactions**: All Illustrator alerts, prompts, and dialogs are now suppressed
- **Creative Cloud Library Integration**: Automatically updates matching CC Library files with timestamped layers
- **Terminal-based output**: All information is displayed in terminal instead of Illustrator alerts
- **Automated save/close**: Documents are saved and closed without any prompts

### New Features
- **CC Library Auto-Update**: After processing, searches for matching files in Creative Cloud Libraries and copies the timestamped layer
- **Database-Driven Search**: Uses DXFya3toCCLibrary's SQLite database for instant file lookups (0.03s)
- **Automatic Sync**: Changes to CC Library files automatically sync to Creative Cloud
- Dialog suppression: Illustrator's user interaction level is set to "never interact"
- Save without dialogs: Uses `without dialogs` option for save operations
- Close without prompts: Documents close without asking about unsaved changes

### Improvements
- Canvas size information now outputs to terminal instead of showing alerts
- Enhanced error handling for dialog suppression and CC Library operations
- Better compatibility with different Illustrator versions
- Non-blocking CC Library updates (continues if CC file not found)

### Technical Changes
- Added `set user interaction level of application preferences to never interact` to all AppleScript operations
- Updated save operation to use `without dialogs` option
- Updated close operation to use `saving no` to prevent prompts
- All ExtendScript operations continue to work without user interaction
- Integrated with DXFya3toCCLibrary database for CC file lookups
- New ExtendScript for layer copying between documents

### Files Added
- `DXFya3toCCLibrary/update_cc_library_file.py` - CC Library update integration

### Files Modified
- `dxf_to_ai_converter_working.py` - Added dialog suppression and CC Library integration
- `DXFya3_Workflow_Documentation.md` - Documented CC Library update step
- `README.md` - Updated to reflect Version 3.1 features including CC integration
- `CHANGELOG.md` - This file
- `VERSION` - Version tracking file

## Version 3.0 - Initial Working Version

### Features
- DXF file monitoring and automatic conversion
- Canvas size checking
- Layer duplication with timestamping
- Path extraction from GroupItems
- Path joining operations
- Terminal-based reporting

---

*For detailed workflow information, see DXFya3_Workflow_Documentation.md*

