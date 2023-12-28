import ifcopenshell
import ifcopenshell.geom
import math
from ifcopenshell.api import run


file = ifcopenshell.file()
model = file

# All projects must have one IFC Project element
project = run("root.create_entity", model, ifc_class="IfcProject", name="My Project")


# Create a semicircle profile
center = file.createIfcCartesianPoint((0., 0., 0.))
axis2placement = file.createIfcAxis2Placement3D(center)
semicircle = file.createIfcCircleProfileDef("AREA", None, axis2placement, 1.0)

# Create a revolved area solid
axis = file.createIfcDirection((0., 0., 1.))
axis1placement = file.createIfcAxis1Placement(center, axis)
revolved_area_solid = file.createIfcRevolvedAreaSolid(semicircle, axis1placement, axis, math.radians(360))

# Create a shape representation
from ifcopenshell.util import shape_builder
builder = shape_builder.ShapeBuilder(model)
model3d = run("context.add_context", model, context_type="Model")
body = run("context.add_context", model,
    context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model3d)

# items = file.createIfcRepresentationItem(revolved_area_solid)
# context_of_items = file.by_type("IfcGeometricRepresentationContext")[0]
#representation = file.createIfcShapeRepresentation(body, "Body", "SweptSolid", [revolved_area_solid])
representation = builder.get_representation(body, revolved_area_solid)

# Create a building element proxy
local_placement = file.createIfcLocalPlacement()
building_element_proxy = file.createIfcBuildingElementProxy(ifcopenshell.guid.new(), None, "Sphere", "A 3D sphere", None, local_placement, representation, None)
#building_element_proxy = run("root.create_entity", model, ifc_class="Ifcbuildingelementproxy") # IfcFurniture

# Write the IFC file
file.write("./data/example5_sphere.ifc")