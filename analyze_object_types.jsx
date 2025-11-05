// ExtendScript to analyze object types in the timestamped layer
// Identifies what types of objects are present in the layer

try {
    var doc = app.activeDocument;
    if (doc == null) {
        "ERROR: No active document";
    } else {
        // Get the timestamped layer (should be the first layer)
        var timestampedLayer = doc.layers[0];
        var layerName = timestampedLayer.name;
        
        // Count objects by type
        var objectTypes = {};
        var totalObjects = timestampedLayer.pageItems.length;
        
        for (var i = 0; i < timestampedLayer.pageItems.length; i++) {
            var item = timestampedLayer.pageItems[i];
            var typeName = item.typename;
            
            if (objectTypes[typeName]) {
                objectTypes[typeName]++;
            } else {
                objectTypes[typeName] = 1;
            }
        }
        
        // Build result string
        var result = "OBJECT TYPE ANALYSIS for layer '" + layerName + "':\n";
        result += "Total objects: " + totalObjects + "\n";
        result += "Object breakdown:\n";
        
        for (var type in objectTypes) {
            result += "  - " + type + ": " + objectTypes[type] + " objects\n";
        }
        
        // Check specifically for path-related objects
        var pathRelatedCount = 0;
        var pathRelatedTypes = [];
        
        for (var i = 0; i < timestampedLayer.pageItems.length; i++) {
            var item = timestampedLayer.pageItems[i];
            var typeName = item.typename;
            
            // Check if it's a path-related object
            if (typeName == "PathItem" || 
                typeName == "CompoundPathItem" || 
                typeName == "GroupItem" ||
                (item.pathPoints && item.pathPoints.length > 0)) {
                pathRelatedCount++;
                
                // Check if type already exists in array (ExtendScript compatible)
                var typeExists = false;
                for (var k = 0; k < pathRelatedTypes.length; k++) {
                    if (pathRelatedTypes[k] == typeName) {
                        typeExists = true;
                        break;
                    }
                }
                if (!typeExists) {
                    pathRelatedTypes.push(typeName);
                }
            }
        }
        
        result += "\nPath-related objects: " + pathRelatedCount + "\n";
        if (pathRelatedTypes.length > 0) {
            result += "Path-related types: " + pathRelatedTypes.join(", ");
        }
        
        result;
    }
} catch (error) {
    "ERROR: " + error.toString();
}
