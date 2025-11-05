# Changelog

## Version 3.1 - Fully Automated (No User Interaction)

### Major Changes
- **Eliminated all user interactions**: All Illustrator alerts, prompts, and dialogs are now suppressed
- **Terminal-based output**: All information is displayed in terminal instead of Illustrator alerts
- **Automated save/close**: Documents are saved and closed without any prompts

### New Features
- Dialog suppression: Illustrator's user interaction level is set to "never interact"
- Save without dialogs: Uses `without dialogs` option for save operations
- Close without prompts: Documents close without asking about unsaved changes

### Improvements
- Canvas size information now outputs to terminal instead of showing alerts
- Enhanced error handling for dialog suppression
- Better compatibility with different Illustrator versions

### Technical Changes
- Added `set user interaction level of application preferences to never interact` to all AppleScript operations
- Updated save operation to use `without dialogs` option
- Updated close operation to use `saving no` to prevent prompts
- All ExtendScript operations continue to work without user interaction

### Files Modified
- `dxf_to_ai_converter_working.py` - Added dialog suppression throughout
- `README.md` - Updated to reflect Version 3.1 features
- `VERSION` - Created version tracking file

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
