// ExtendScript to create timestamped layer and copy all objects to it
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
        
        // Clear any existing selection
        doc.selection = null;
        
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
        
        // Select all items if any exist
        if (allItems.length > 0) {
            doc.selection = allItems;
            
            // Copy selection to clipboard
            app.copy();
            
            // Clear selection before pasting
            doc.selection = null;
            
            // Select the new layer
            doc.activeLayer = newLayer;
            
            // Paste into new layer at original position
            app.paste();
            
            // Delete all original layers except the new one
            var layersToDelete = [];
            for (var k = 0; k < doc.layers.length; k++) {
                if (doc.layers[k] != newLayer) {
                    layersToDelete.push(doc.layers[k]);
                }
            }
            
            // Delete original layers (in reverse order to avoid index issues)
            for (var m = layersToDelete.length - 1; m >= 0; m--) {
                layersToDelete[m].remove();
            }
            
            // Return success message
            "SUCCESS: Created layer '" + layerName + "' with " + allItems.length + " objects (total found: " + totalObjects + ")";
        } else {
            "WARNING: No objects found to copy (total objects in doc: " + totalObjects + ")";
        }
    }
} catch (error) {
    "ERROR: " + error.toString();
}
