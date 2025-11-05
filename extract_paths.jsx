// ExtendScript to extract PathItems from GroupItems without ungrouping
try {
    var doc = app.activeDocument;
    if (doc == null) {
        "ERROR: No active document";
    } else {
        var timestampedLayer = doc.layers[0];
        var layerName = timestampedLayer.name;
        
        var initialObjectCount = timestampedLayer.pageItems.length;
        var extractedPaths = 0;
        var extractedPathItems = [];
        
        // Extract PathItems from GroupItems
        for (var i = 0; i < timestampedLayer.pageItems.length; i++) {
            var item = timestampedLayer.pageItems[i];
            if (item.typename == "GroupItem") {
                // Check if group has exactly 1 PathItem
                if (item.pageItems.length == 1 && item.pageItems[0].typename == "PathItem") {
                    var pathItem = item.pageItems[0];
                    
                    // Duplicate the PathItem to the layer
                    var duplicatedPath = pathItem.duplicate(timestampedLayer, ElementPlacement.PLACEATEND);
                    extractedPathItems.push(duplicatedPath);
                    extractedPaths++;
                }
            }
        }
        
        // Count final objects
        var finalObjectCount = timestampedLayer.pageItems.length;
        
        "SUCCESS: Extracted " + extractedPaths + " PathItems from GroupItems in layer '" + layerName + "'. Objects before: " + initialObjectCount + ", Objects after: " + finalObjectCount + ". PathItems available for joining: " + extractedPaths;
    }
} catch (error) {
    "ERROR: " + error.toString();
}

