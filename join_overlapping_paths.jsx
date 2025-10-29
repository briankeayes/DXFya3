// ExtendScript to find and join overlapping path endpoints
// Starting from top-left of document, finds first overlapping paths and joins them

try {
    var doc = app.activeDocument;
    if (doc == null) {
        "ERROR: No active document";
    } else {
        // Get the timestamped layer (should be the first layer)
        var timestampedLayer = doc.layers[0];
        var layerName = timestampedLayer.name;
        
        // Count objects in the layer
        var totalObjects = timestampedLayer.pageItems.length;
        
        if (totalObjects < 2) {
            "INFO: Not enough objects to find overlaps. Found " + totalObjects + " objects in layer '" + layerName + "'";
        } else {
            // Find all path items in the layer
            var pathItems = [];
            for (var i = 0; i < timestampedLayer.pageItems.length; i++) {
                if (timestampedLayer.pageItems[i].typename == "PathItem") {
                    pathItems.push(timestampedLayer.pageItems[i]);
                }
            }
            
            if (pathItems.length < 2) {
                "INFO: Not enough path items to find overlaps. Found " + pathItems.length + " path items in layer '" + layerName + "'";
            } else {
                // Sort paths by position (top-left to bottom-right)
                pathItems.sort(function(a, b) {
                    // Sort by Y position first (top to bottom), then by X position (left to right)
                    var yDiff = a.position[1] - b.position[1];
                    if (Math.abs(yDiff) > 1) { // If Y difference is significant
                        return yDiff;
                    }
                    return a.position[0] - b.position[0]; // Then by X position
                });
                
                var joinedPaths = 0;
                var tolerance = 0.1; // Tolerance for endpoint overlap detection
                
                // Check for overlapping endpoints
                for (var i = 0; i < pathItems.length - 1; i++) {
                    var path1 = pathItems[i];
                    if (path1 == null) continue; // Skip if path was deleted
                    
                    for (var j = i + 1; j < pathItems.length; j++) {
                        var path2 = pathItems[j];
                        if (path2 == null) continue; // Skip if path was deleted
                        
                        // Get path points
                        var path1Points = getPathPoints(path1);
                        var path2Points = getPathPoints(path2);
                        
                        // Check for overlapping endpoints
                        var overlap = findOverlappingEndpoints(path1Points, path2Points, tolerance);
                        
                        if (overlap.found) {
                            // Join the paths
                            var success = joinPaths(path1, path2, overlap);
                            if (success) {
                                joinedPaths++;
                                // Remove the second path from our array since it's been merged
                                pathItems[j] = null;
                                break; // Move to next path1
                            }
                        }
                    }
                }
                
                "SUCCESS: Found " + totalObjects + " objects in layer '" + layerName + "'. Analyzed " + pathItems.length + " path items. Joined " + joinedPaths + " overlapping paths.";
            }
        }
    }
} catch (error) {
    "ERROR: " + error.toString();
}

// Helper function to get path points
function getPathPoints(pathItem) {
    var points = [];
    if (pathItem.pathPoints && pathItem.pathPoints.length > 0) {
        for (var i = 0; i < pathItem.pathPoints.length; i++) {
            var point = pathItem.pathPoints[i];
            points.push({
                anchor: point.anchor,
                leftDirection: point.leftDirection,
                rightDirection: point.rightDirection,
                pointType: point.pointType
            });
        }
    }
    return points;
}

// Helper function to find overlapping endpoints
function findOverlappingEndpoints(points1, points2, tolerance) {
    if (points1.length == 0 || points2.length == 0) {
        return {found: false};
    }
    
    // Get endpoints (first and last points)
    var end1a = points1[0].anchor;
    var end1b = points1[points1.length - 1].anchor;
    var end2a = points2[0].anchor;
    var end2b = points2[points2.length - 1].anchor;
    
    // Check all combinations of endpoints
    var combinations = [
        {end1: end1a, end2: end2a, path1Index: 0, path2Index: 0},
        {end1: end1a, end2: end2b, path1Index: 0, path2Index: points2.length - 1},
        {end1: end1b, end2: end2a, path1Index: points1.length - 1, path2Index: 0},
        {end1: end1b, end2: end2b, path1Index: points1.length - 1, path2Index: points2.length - 1}
    ];
    
    for (var i = 0; i < combinations.length; i++) {
        var combo = combinations[i];
        var distance = Math.sqrt(
            Math.pow(combo.end1[0] - combo.end2[0], 2) + 
            Math.pow(combo.end1[1] - combo.end2[1], 2)
        );
        
        if (distance <= tolerance) {
            return {
                found: true,
                path1Index: combo.path1Index,
                path2Index: combo.path2Index,
                distance: distance
            };
        }
    }
    
    return {found: false};
}

// Helper function to join two paths
function joinPaths(path1, path2, overlap) {
    try {
        // Create a compound path to merge the two paths
        var compoundPath = path1.parent.compoundPathItems.add();
        
        // Add both paths to the compound path
        path1.move(compoundPath, ElementPlacement.PLACEATEND);
        path2.move(compoundPath, ElementPlacement.PLACEATEND);
        
        // Release the compound path to merge them
        compoundPath.release();
        
        return true;
    } catch (error) {
        return false;
    }
}
