// ExtendScript for layer duplication with datestamp
// This script copies all objects from layer 0 to a new layer with datestamp, then deletes layer 0

try {
    // Get the active document (first document if multiple are open)
    var doc = app.documents[0];
    
    // Get current date and time
    var currentDate = new Date();
    var year = currentDate.getFullYear();
    var month = (currentDate.getMonth() + 1).toString().padStart(2, '0');
    var day = currentDate.getDate().toString().padStart(2, '0');
    var hours = currentDate.getHours().toString().padStart(2, '0');
    var minutes = currentDate.getMinutes().toString().padStart(2, '0');
    var seconds = currentDate.getSeconds().toString().padStart(2, '0');
    
    var dateString = year + "-" + month + "-" + day + "_" + hours + "-" + minutes + "-" + seconds;
    
    // Select all objects on layer 0 (first layer)
    var layer0 = doc.layers[0];
    
    // Clear any existing selection first
    doc.selection = null;
    
    // Select all art items on layer 0
    for (var i = 0; i < layer0.pageItems.length; i++) {
        layer0.pageItems[i].selected = true;
    }
    
    // Copy selection
    app.copy();
    
    // Create new layer
    var newLayer = doc.layers.add();
    newLayer.name = dateString;
    
    // Move new layer to front (top of layer stack)
    newLayer.move(doc.layers[0], ElementPlacement.PLACEAFTER);
    
    // Paste into new layer
    app.paste();
    
    // Delete original layer 0 (now the second layer)
    doc.layers[1].remove();
    
    // Return success message
    "Layer duplication completed successfully";
    
} catch (error) {
    "Error: " + error.toString();
}
