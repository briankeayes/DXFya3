// Diagnostic script to analyze PathItems and test overlap detection
try {
    var doc = app.activeDocument;
    if (doc == null) {
        "ERROR: No active document";
    } else {
        var timestampedLayer = doc.layers[0];
        var layerName = timestampedLayer.name;
        
        var result = "PATH ANALYSIS for layer '" + layerName + "':\n";
        
        // Find all PathItems (should be the extracted ones)
        var pathItems = [];
        for (var i = 0; i < timestampedLayer.pageItems.length; i++) {
            if (timestampedLayer.pageItems[i].typename == "PathItem") {
                pathItems.push(timestampedLayer.pageItems[i]);
            }
        }
        
        result += "Total PathItems found: " + pathItems.length + "\n\n";
        
        // Analyze first 5 PathItems
        for (var i = 0; i < Math.min(5, pathItems.length); i++) {
            var path = pathItems[i];
            result += "Path " + (i + 1) + ":\n";
            result += "  - Points: " + (path.pathPoints ? path.pathPoints.length : 0) + "\n";
            result += "  - Position: [" + path.position[0] + ", " + path.position[1] + "]\n";
            
            if (path.pathPoints && path.pathPoints.length >= 2) {
                var startPoint = path.pathPoints[0].anchor;
                var endPoint = path.pathPoints[path.pathPoints.length - 1].anchor;
                result += "  - Start: [" + startPoint[0] + ", " + startPoint[1] + "]\n";
                result += "  - End: [" + endPoint[0] + ", " + endPoint[1] + "]\n";
            }
            result += "\n";
        }
        
        // Test overlap detection between first few paths
        result += "OVERLAP TESTING:\n";
        var tolerance = 0.1;
        var overlapCount = 0;
        
        for (var i = 0; i < Math.min(3, pathItems.length); i++) {
            for (var j = i + 1; j < Math.min(3, pathItems.length); j++) {
                var path1 = pathItems[i];
                var path2 = pathItems[j];
                
                if (path1.pathPoints && path2.pathPoints && 
                    path1.pathPoints.length >= 2 && path2.pathPoints.length >= 2) {
                    
                    var p1Start = path1.pathPoints[0].anchor;
                    var p1End = path1.pathPoints[path1.pathPoints.length - 1].anchor;
                    var p2Start = path2.pathPoints[0].anchor;
                    var p2End = path2.pathPoints[path2.pathPoints.length - 1].anchor;
                    
                    // Check all endpoint combinations
                    var distances = [
                        Math.sqrt(Math.pow(p1Start[0] - p2Start[0], 2) + Math.pow(p1Start[1] - p2Start[1], 2)),
                        Math.sqrt(Math.pow(p1Start[0] - p2End[0], 2) + Math.pow(p1Start[1] - p2End[1], 2)),
                        Math.sqrt(Math.pow(p1End[0] - p2Start[0], 2) + Math.pow(p1End[1] - p2Start[1], 2)),
                        Math.sqrt(Math.pow(p1End[0] - p2End[0], 2) + Math.pow(p1End[1] - p2End[1], 2))
                    ];
                    
                    var minDistance = Math.min.apply(Math, distances);
                    result += "Path " + (i + 1) + " vs Path " + (j + 1) + ": min distance = " + minDistance.toFixed(3) + "\n";
                    
                    if (minDistance <= tolerance) {
                        overlapCount++;
                        result += "  -> OVERLAP DETECTED!\n";
                    }
                }
            }
        }
        
        result += "\nSUMMARY:\n";
        result += "- PathItems analyzed: " + Math.min(5, pathItems.length) + "\n";
        result += "- Overlaps found: " + overlapCount + "\n";
        result += "- Tolerance used: " + tolerance + "\n";
        
        result;
    }
} catch (error) {
    "ERROR: " + error.toString();
}

