// run like /System/Library/Frameworks/JavaVM.framework/Commands/java -jar /Applications/Fiji.app/jars/ij-1.49q.jar -batch generate_fixtures.js

importClass(Packages.ij.gui.Roi);
importClass(Packages.ij.gui.PolygonRoi);
importClass(Packages.ij.IJ);
importClass(Packages.ij.ImagePlus);
importClass(Packages.ij.io.RoiEncoder);
importClass(Packages.ij.process.ByteProcessor);

var subpixel_rectangle = new Roi(4, 5, 4, 5);
RoiEncoder.save(subpixel_rectangle, "subpixel_rectangle.roi");

var integer_rectangle = new Roi["(int,int,int,int)"](4, 5, 4, 5);
RoiEncoder.save(integer_rectangle, "integer_rectangle.roi");

var x = new java.lang.reflect.Array.newInstance(java.lang.Float.TYPE, 100);
var y = new java.lang.reflect.Array.newInstance(java.lang.Float.TYPE, 100);

for(var i = 0; i < 100; ++i) {
	x[i] = 10 + Math.cos(i/100.0 * 2*Math.PI);
	y[i] = 15 + Math.sin(i/100.0 * 2*Math.PI);
}

freehand_circle = PolygonRoi(x, y, 100, Roi.FREEROI);
RoiEncoder.save(freehand_circle, "freehand_circle.roi");

var xi = new java.lang.reflect.Array.newInstance(java.lang.Integer.TYPE, 3);
var yi = new java.lang.reflect.Array.newInstance(java.lang.Integer.TYPE, 3);
xi[0] = 1; xi[1] = 10; xi[2] = 10;
yi[0] = 1; yi[1] = 10; yi[2] = 1;

freehand_integer = PolygonRoi(xi, yi, 3, Roi.FREEROI);
RoiEncoder.save(freehand_integer, "freehand_integer.roi");

"Success";
