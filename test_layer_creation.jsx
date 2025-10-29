// Simple test ExtendScript - just create a layer
try {
    var doc = app.activeDocument;
    if (doc == null) {
        "ERROR: No active document";
    } else {
        var newLayer = doc.layers.add();
        newLayer.name = "TestLayer_" + new Date().getTime();
        "SUCCESS: Created test layer '" + newLayer.name + "'";
    }
} catch (error) {
    "ERROR: " + error.toString();
}
