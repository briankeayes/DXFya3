// ExtendScript to ungroup all objects in the timestamped layer (recursively until no more groups)
try {
    var doc = app.activeDocument;
    if (doc == null) {
        "ERROR: No active document";
    } else {
        var timestampedLayer = doc.layers[0];
        var layerName = timestampedLayer.name;
        
        var initialObjectCount = timestampedLayer.pageItems.length;
        var totalUngrouped = 0;
        var passCount = 0;
        var maxPasses = 10; // Safety limit to prevent infinite loops
        
        // Keep ungrouping until no more groups are found
        while (passCount < maxPasses) {
            passCount++;
            var groupsFound = 0;
            var ungroupedThisPass = 0;
            
            // Count groups first
            for (var i = 0; i < timestampedLayer.pageItems.length; i++) {
                if (timestampedLayer.pageItems[i].typename == "GroupItem") {
                    groupsFound++;
                }
            }
            
            if (groupsFound == 0) {
                break; // No more groups found, we're done
            }
            
            // Ungroup all groups (iterate backwards to avoid index issues)
            for (var i = timestampedLayer.pageItems.length - 1; i >= 0; i--) {
                var item = timestampedLayer.pageItems[i];
                if (item.typename == "GroupItem") {
                    try {
                        // Make sure the group is visible and unlocked
                        item.visible = true;
                        item.locked = false;
                        
                        // Use the correct ExtendScript method for ungrouping
                        item.move(timestampedLayer, ElementPlacement.PLACEATEND);
                        
                        // Alternative approach: release the group
                        if (item.release) {
                            item.release();
                        }
                        
                        ungroupedThisPass++;
                        totalUngrouped++;
                    } catch (error) {
                        // Try alternative ungrouping method
                        try {
                            // Select and ungroup using menu command approach
                            doc.selection = null;
                            item.selected = true;
                            app.executeMenuCommand("ungroup");
                            ungroupedThisPass++;
                            totalUngrouped++;
                        } catch (error2) {
                            // Skip if all ungrouping methods fail
                        }
                    }
                }
            }
            
            // Safety check - if we didn't ungroup anything, break to avoid infinite loop
            if (ungroupedThisPass == 0) {
                break;
            }
        }
        
        // Count final objects
        var finalObjectCount = timestampedLayer.pageItems.length;
        
        "SUCCESS: Completed " + passCount + " ungrouping passes. Ungrouped " + totalUngrouped + " groups total in layer '" + layerName + "'. Objects before: " + initialObjectCount + ", Objects after: " + finalObjectCount + ". Groups remaining: " + groupsFound;
    }
} catch (error) {
    "ERROR: " + error.toString();
}
