// Illustrator script to create a new A4 document with a centered circle
// Run this script in Illustrator

// Create a new A4 document
var doc = app.documents.addDocument("RGB", new Array(595.28, 841.89)); // A4 size in points

// Get the active document
var activeDoc = app.activeDocument;

// Calculate center point of the page
var pageWidth = activeDoc.width;
var pageHeight = activeDoc.height;
var centerX = pageWidth / 2;
var centerY = pageHeight / 2;

// Create a circle centered on the page
// Circle radius (adjust as needed)
var radius = 50; // points

// Create the circle
var circle = activeDoc.pathItems.ellipse(centerY + radius, centerX - radius, radius * 2, radius * 2);

// Set circle properties
circle.filled = true;
circle.fillColor = activeDoc.swatches[0]; // Use first swatch color
circle.stroked = true;
circle.strokeColor = activeDoc.swatches[1]; // Use second swatch color
circle.strokeWidth = 2;

// Center the circle on the page
circle.position = [centerX - radius, centerY - radius];

// Show a message
alert("Created a centered circle on A4 page!");
