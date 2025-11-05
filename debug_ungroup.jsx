// Debug script to understand why ungrouping isn't working
try {
    var doc = app.activeDocument;
    if (doc == null) {
        "ERROR: No active document";
    } else {
        var timestampedLayer = doc.layers[0];
        var layerName = timestampedLayer.name;
        
        var result = "DEBUG UNGROUPING for layer '" + layerName + "':\n";
        result += "Total objects: " + timestampedLayer.pageItems.length + "\n\n";
        
        var groupCount = 0;
        var ungroupAttempts = 0;
        var ungroupSuccesses = 0;
        
        // Check first few groups and try to ungroup them
        for (var i = 0; i < Math.min(3, timestampedLayer.pageItems.length); i++) {
            var item = timestampedLayer.pageItems[i];
            result += "Object " + (i + 1) + ": " + item.typename + "\n";
            
            if (item.typename == "GroupItem") {
                groupCount++;
                result += "  - GroupItem found\n";
                result += "  - Group has " + item.pageItems.length + " items\n";
                
                // Try to ungroup this specific group
                try {
                    result += "  - Attempting to ungroup...\n";
                    ungroupAttempts++;
                    
                    // Check if group is locked or has other restrictions
                    result += "  - Group locked: " + (item.locked ? "YES" : "NO") + "\n";
                    result += "  - Group visible: " + (item.visible ? "YES" : "NO") + "\n";
                    
                    item.ungroup();
                    ungroupSuccesses++;
                    result += "  - Ungroup SUCCESS!\n";
                    
                } catch (error) {
                    result += "  - Ungroup FAILED: " + error.toString() + "\n";
                }
            }
            result += "\n";
        }
        
        result += "SUMMARY:\n";
        result += "- Groups found: " + groupCount + "\n";
        result += "- Ungroup attempts: " + ungroupAttempts + "\n";
        result += "- Ungroup successes: " + ungroupSuccesses + "\n";
        result += "- Final object count: " + timestampedLayer.pageItems.length + "\n";
        
        result;
    }
} catch (error) {
    "ERROR: " + error.toString();
}

