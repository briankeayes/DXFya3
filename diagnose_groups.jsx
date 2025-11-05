// Diagnostic script to see what's inside GroupItems
try {
    var doc = app.activeDocument;
    if (doc == null) {
        "ERROR: No active document";
    } else {
        var timestampedLayer = doc.layers[0];
        var layerName = timestampedLayer.name;
        var totalObjects = timestampedLayer.pageItems.length;
        
        var result = "GROUP ANALYSIS for layer '" + layerName + "':\n";
        result += "Total objects: " + totalObjects + "\n\n";
        
        var pathCount = 0;
        var groupCount = 0;
        var emptyGroupCount = 0;
        
        for (var i = 0; i < Math.min(5, timestampedLayer.pageItems.length); i++) { // Check first 5 groups
            var item = timestampedLayer.pageItems[i];
            result += "Group " + (i + 1) + " (" + item.typename + "):\n";
            
            if (item.typename == "GroupItem") {
                groupCount++;
                result += "  - Group has " + item.pageItems.length + " items\n";
                
                if (item.pageItems.length == 0) {
                    emptyGroupCount++;
                    result += "  - EMPTY GROUP\n";
                } else {
                    // Show first few items in the group
                    for (var j = 0; j < Math.min(3, item.pageItems.length); j++) {
                        var subItem = item.pageItems[j];
                        result += "    - Item " + (j + 1) + ": " + subItem.typename + "\n";
                        
                        if (subItem.typename == "PathItem") {
                            pathCount++;
                            result += "      - PathItem found! Has " + (subItem.pathPoints ? subItem.pathPoints.length : 0) + " points\n";
                        }
                    }
                    
                    if (item.pageItems.length > 3) {
                        result += "    - ... and " + (item.pageItems.length - 3) + " more items\n";
                    }
                }
            } else {
                result += "  - Not a GroupItem: " + item.typename + "\n";
            }
            result += "\n";
        }
        
        result += "SUMMARY:\n";
        result += "- Groups checked: " + groupCount + "\n";
        result += "- Empty groups: " + emptyGroupCount + "\n";
        result += "- PathItems found: " + pathCount + "\n";
        
        result;
    }
} catch (error) {
    "ERROR: " + error.toString();
}


