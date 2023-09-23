from iges.export import IGESExport
from iges.entities import IGESPoint, IGESLine, IGESPlane, IGESExtruded, IGESSolid

# Create a new IGES export object
iges_export = IGESExport()

# Define points
point1 = IGESPoint(x=0.0, y=0.0, z=0.0)
point2 = IGESPoint(x=1.0, y=0.0, z=0.0)
point3 = IGESPoint(x=1.0, y=1.0, z=0.0)
point4 = IGESPoint(x=0.5, y=1.5, z=0.0)
point5 = IGESPoint(x=0.0, y=1.0, z=0.0)
point6 = IGESPoint(x=0.0, y=0.0, z=2.0)

# Create lines connecting the points
line1 = IGESLine(start_point=point1, end_point=point2)
line2 = IGESLine(start_point=point2, end_point=point3)
line3 = IGESLine(start_point=point3, end_point=point4)
line4 = IGESLine(start_point=point4, end_point=point5)
line5 = IGESLine(start_point=point5, end_point=point1)

# Create a plane from the lines
plane1 = IGESPlane(lines=[line1, line2, line3, line4, line5])

# Create an extruded shape from the plane
extruded1 = IGESExtruded(plane=plane1, direction=IGESPoint(x=0.0, y=0.0, z=1.0), depth=2.0)

# Create a solid from the extruded shape
solid1 = IGESSolid(surface=extruded1)

# Add the solid to the IGES export object
iges_export.add_entity(solid1)

# Save the IGES file
iges_export.save("extruded_shape.igs")
