// Simplified path joining script with better error handling
try {
    var doc = app.activeDocument;
    if (doc == null) {
        "ERROR: No active document";
    } else {
        var timestampedLayer = doc.layers[0];
        var layerName = timestampedLayer.name;
        
        // Find all PathItems
        var pathItems = [];
        for (var i = 0; i < timestampedLayer.pageItems.length; i++) {
            var item = timestampedLayer.pageItems[i];
            if (item.typename == "PathItem") {
                pathItems.push(item);
            }
        }
        
        if (pathItems.length < 2) {
            "INFO: Not enough PathItems to join. Found " + pathItems.length + " PathItems in layer '" + layerName + "'";
        } else {
            var joinedPaths = 0;
            var tolerance = 1.0; // Increased tolerance for better detection
            
            // Simple approach: try to join paths by selecting and using Illustrator's join command
            for (var i = 0; i < pathItems.length - 1; i++) {
                var path1 = pathItems[i];
                if (path1 == null) continue;
                
                for (var j = i + 1; j < pathItems.length; j++) {
                    var path2 = pathItems[j];
                    if (path2 == null) continue;
                    
                    try {
                        // Check if paths are close enough to join
                        var distance = Math.sqrt(
                            Math.pow(path1.position[0] - path2.position[0], 2) + 
                            Math.pow(path1.position[1] - path2.position[1], 2)
                        );
                        
                        if (distance <= tolerance) {
                            // Select both paths
                            doc.selection = null;
                            path1.selected = true;
                            path2.selected = true;
                            
                            // Try to join them using Illustrator's join command
                            try {
                                app.executeMenuCommand("join");
                                joinedPaths++;
                                
                                // Remove the second path from our array since it's been merged
                                pathItems[j] = null;
                                break; // Move to next path1
                            } catch (joinError) {
                                // Join failed, continue
                            }
                        }
                    } catch (error) {
                        // Skip if there's an error
                    }
                }
            }
            
            "SUCCESS: Found " + pathItems.length + " PathItems in layer '" + layerName + "'. Attempted to join " + joinedPaths + " path pairs using Illustrator's join command.";
        }
    }
} catch (error) {
    "ERROR: " + error.toString();
}

