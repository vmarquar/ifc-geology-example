import numpy as np
import ifcopenshell
from ifcopenshell.api import run
import ifcopenshell.geom
import ifcopenshell.validate
import ifcopenshell.util
import time
import random

def create_sphere_representation(model, radius: float = 500.0):
    """ ALTERNATIVE WAYS OF CREATING REPRESENTATIONS
    from ifcopenshell.util import shape_builder
    import mathutils
    builder = shape_builder.ShapeBuilder(model)
    outer_curve = builder.polyline([(0.,0.), (100.,0.), (100.,50.), (51.2,98.7), (18.5,105.3), (0.,77.5)], arc_points=[4], closed=True)
    inner_curve = builder.circle((50.,50.), radius=10.)
    semi_circle = builder.polyline([(0.,0.), (50.,50.), (100.,0.)], arc_points=[1], closed=True)
    arbitrary_profile = builder.profile(outer_curve, inner_curves=[inner_curve], name="Arbitrary")
    semicircle_profile = builder.profile(semi_circle, name="Arc")
    rebar_curve = builder.polyline([(0., 0., 0.), (100., 0., 0.), (171., 29., 0.), (200., 100., 0.), (200., 200., 0.)], arc_points=[2])
    swept_rebar_curve = builder.create_swept_disk_solid(rebar_curve, 10)
    semiarc_extrusion = builder.extrude(semi_circle, **builder.extrude_kwargs(axis='X'))
    profile = model.create_entity("IfcCircleProfileDef", ProfileName="example_profile_name_eg_sphere300", ProfileType="AREA", Radius=300)

    # A profile-based representation, 1 meter long
    semiarc_representation = builder.get_representation(context=body, items=semiarc_extrusion)
    cylinder_representation = run("geometry.add_profile_representation", model, context=body, profile=profile, depth=1.0) # creates a cylinder with 1m height and 300mm radius
    arbitrary_representation = run("geometry.add_profile_representation", model, context=body, profile=arbitrary_profile, depth=1.0) # creates a arbitrary_profile with 1m height 
    semicircle_representation = run("geometry.add_profile_representation", model, context=body, profile=semicircle_profile, depth=1.0) # creates a arbitrary_profile with 1m height 
    swept_rebar_representation = builder.get_representation(body, swept_rebar_curve)

    vertices = [[(0.,0.,0.), (0.,2.,0.), (2.,2.,0.), (2.,0.,0.), (1.,1.,1.)]]
    faces = [[(0,1,2,3), (0,4,1), (1,4,2), (2,4,3), (3,4,0)]]
    pyramide_representation = run("geometry.add_mesh_representation", model, context=body, vertices=vertices, faces=faces)
    """
    # new try - https://blenderbim.org/docs-python/ifcopenshell-python/geometry_creation.html#extruded-area-solid
    location = model.createIfcCartesianPoint((0.0, 0.0, 0.0))
    axis = model.createIfcDirection((0.0, 0.0, radius)) # radius in millimeters
    ref_direction = model.createIfcDirection((radius, 0.0, 0.0))
    axis2placement3d = model.createIfcAxis2Placement3D(location, axis, ref_direction)
    sphere = model.createIfcSphere(Radius=radius, Position=axis2placement3d)
    sphere_representation = model.createIfcShapeRepresentation(ContextOfItems=body, RepresentationIdentifier="Body", RepresentationType="CSG", Items=[sphere])
    return sphere_representation

def create_and_add_style(model: ifcopenshell.file, red: float = 1.0, green: float = 0.5, blue: float = 0.5, transparency: float = 0.5):
    # https://blenderbim.org/docs-python/autoapi/ifcopenshell/api/style/assign_representation_styles/index.html?highlight=style#module-ifcopenshell.api.style.assign_representation_styles
    # Create a new surface style
    # Create a new surface style
    style = ifcopenshell.api.run("style.add_style", model)

    # Create a simple grey shading colour and transparency.
    ifcopenshell.api.run("style.add_surface_style", model,
        style=style, ifc_class="IfcSurfaceStyleShading", attributes={
            "SurfaceColour": { "Name": None, "Red": red, "Green": green, "Blue": blue }, # RGB values between 0 and 1
            "Transparency": transparency, # 0 is opaque, 1 is transparent
        })
    # apply style to wall: ifcopenshell.api.run("style.assign_representation_styles", model, shape_representation=representation, styles=[style])
    return(style)

### 
### 0. Init the Model and assign a Projcet (mandatory)
###
# Create a blank model
model = ifcopenshell.file()
# All projects must have one IFC Project element
project = run("root.create_entity", model, ifc_class="IfcProject", name="My Project")
#site = run("root.create_entity", model, ifc_class="IfcSite", name="My Site")


### 1. set project units
run("unit.assign_unit", model) #TODO: set meters as length units
length = run("unit.add_si_unit", model, unit_type="LENGTHUNIT", prefix=None) # #11=IFCSIUNIT(*,.LENGTHUNIT.,$,.METRE.);

### 2. Add Representation Context for 2D (Plan) and 3D (Model)
model3d = run("context.add_context", model, context_type="Model")
plan = run("context.add_context", model, context_type="Plan")
body = run("context.add_context", model, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model3d)
annotation = run("context.add_context", model, context_type="Plan", context_identifier="Annotation", target_view="PLAN_VIEW", parent=plan)

### 4. create geometry Representations at local placement
style = create_and_add_style(model, red=0.25, green=1.0, blue=0.5, transparency=0.5)
style_1500 = create_and_add_style(model, red=1.0, green=0.25, blue=0.5, transparency=0.5)
sphere_representation = create_sphere_representation(model, radius=750.0)
ifcopenshell.api.run("style.assign_representation_styles", model, shape_representation=sphere_representation, styles=[style])
sphere_representation_1500 = create_sphere_representation(model, radius=1500.0)
ifcopenshell.api.run("style.assign_representation_styles", model, shape_representation=sphere_representation_1500, styles=[style_1500])

### 5. Create an ifc element and then apply the local placement and the geometry Representation to this element
element_type = run("root.create_entity", model, ifc_class="Ifcbuildingelementproxytype") #Variante 2
run("geometry.assign_representation", model, product=element_type, representation=sphere_representation) #Variante 2 - Typ 1
element_type_1500 = run("root.create_entity", model, ifc_class="Ifcbuildingelementproxytype") #Variante 2
run("geometry.assign_representation", model, product=element_type_1500, representation=sphere_representation_1500) #Variante 2 - Typ 2

elements = []
placement_vectors = placement_vectors = [(random.randint(0, 100), random.randint(0, 100), random.randint(0, 100)) for _ in range(1000)]
for idx, placement_vector in enumerate(placement_vectors):
    matrix = np.eye(4)
    matrix[:,3][0:3] = placement_vector
    representation = sphere_representation
    element = run("root.create_entity", model, ifc_class="Ifcbuildingelementproxy")
    elements.append(element)
    run("geometry.edit_object_placement", model, product=element, matrix=matrix, is_si=True)
    #run("geometry.assign_representation", model, product=element, representation=sphere_representation) # Variante 1 (Use this if you have continous data without clusters/bins/categories)
    if(idx % 2  == 0):
        run("type.assign_type", model, related_object=element, relating_type=element_type) #Variante 2 - Typ 1 (Example for even numbers)
    else:
        run("type.assign_type", model, related_object=element, relating_type=element_type_1500) # Variante 2 - Typ 2 (Example for odd numbers)

    ### 7b. simpler way to create a property set and add the properties to it
    pset = ifcopenshell.api.run("pset.add_pset", model, product=element, name="Probenahme PSET")
    ifcopenshell.api.run("pset.edit_pset", model, pset=pset, properties={"Testmethode": "Eimerprobe", "Entnahmetiefe": placement_vector[2], "Proben_Name": f"Probe {placement_vector[0]}-{placement_vector[1]}-{placement_vector[2]}"})

### 7. Validate the model
from logging import getLogger
logger = getLogger("ifcopenshell")
ifcopenshell.validate.validate(model, logger)

### 8. Write the model to disk
model.write("./data/example4_output_model_var2lean.ifc")