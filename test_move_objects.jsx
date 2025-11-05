// Alternative approach: Move objects directly instead of copy/paste
try {
    var doc = app.activeDocument;
    if (doc == null) {
        "ERROR: No active document";
    } else {
        // Get current date and time for layer naming
        var now = new Date();
        var year = now.getFullYear();
        var month = (now.getMonth() + 1 < 10 ? "0" : "") + (now.getMonth() + 1);
        var day = (now.getDate() < 10 ? "0" : "") + now.getDate();
        var hours = (now.getHours() < 10 ? "0" : "") + now.getHours();
        var minutes = (now.getMinutes() < 10 ? "0" : "") + now.getMinutes();
        var seconds = (now.getSeconds() < 10 ? "0" : "") + now.getSeconds();

        var layerName = year + "-" + month + "-" + day + "_" + hours + "-" + minutes + "-" + seconds;
        
        // Count total objects before processing
        var totalObjects = 0;
        for (var i = 0; i < doc.layers.length; i++) {
            totalObjects += doc.layers[i].pageItems.length;
        }
        
        // Create a new layer
        var newLayer = doc.layers.add();
        newLayer.name = layerName;
        
        // Move new layer to the top
        newLayer.move(doc.layers[0], ElementPlacement.PLACEAFTER);
        
        // Collect all page items from all layers (except the new one)
        var allItems = [];
        for (var i = 0; i < doc.layers.length; i++) {
            var layer = doc.layers[i];
            if (layer != newLayer) { // Don't include the new layer
                for (var j = 0; j < layer.pageItems.length; j++) {
                    allItems.push(layer.pageItems[j]);
                }
            }
        }
        
        // Move all items to the new layer (keeping originals)
        if (allItems.length > 0) {
            // Copy each item to the new layer instead of moving
            for (var i = 0; i < allItems.length; i++) {
                // Duplicate the item to the new layer
                var duplicatedItem = allItems[i].duplicate(newLayer, ElementPlacement.PLACEATEND);
            }
            
            // Count objects in the new layer after duplication
            var objectsInNewLayer = newLayer.pageItems.length;
            
            // Return detailed success message
            "SUCCESS: Created layer '" + layerName + "' with " + objectsInNewLayer + " objects. Original layers preserved. Total objects processed: " + allItems.length + " (total found in document: " + totalObjects + ")";
        } else {
            "WARNING: No objects found to copy (total objects in doc: " + totalObjects + ")";
        }
    }
} catch (error) {
    "ERROR: " + error.toString();
}
