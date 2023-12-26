import numpy as np
import ifcopenshell
from ifcopenshell.api import run
import ifcopenshell.geom
import ifcopenshell.validate
import ifcopenshell.util 
import time
import random

### 
### 0. Init the Model and assign a Projcet (mandatory)
###
# Create a blank model
model = ifcopenshell.file()
# All projects must have one IFC Project element
project = run("root.create_entity", model, ifc_class="IfcProject", name="My Project")
#site = run("root.create_entity", model, ifc_class="IfcSite", name="My Site")


###
### 1. set project units
###
# Geometry is optional in IFC, but because we want to use geometry in this example, let's define units
# Assigning without arguments defaults to metric units
run("unit.assign_unit", model) #TODO: set meters as length units
length = run("unit.add_si_unit", model, unit_type="LENGTHUNIT", prefix=None) # #11=IFCSIUNIT(*,.LENGTHUNIT.,$,.METRE.);



###
### 2. create local placement ("= local origin" or "insertion point")
###
# XAxis_X, YAxis_X, ZAxis_X, X
# XAxis_Y, YAxis_Y, ZAxis_Y, Y
# XAxis_Z, YAxis_Z, ZAxis_Z, Z
# 0,       0,       0,       1 <- Notice how the last line is always fixed to 0, 0, 0, 1
# identity_matrix = np.eye(4)
#matrix = ifcopenshell.util.placement.rotation(90, "Z") @ matrix # optional: rotation around Z axis
# Set the X, Y, Z coordinates. Notice how we rotate first then translate.
# This is because the rotation origin is always at 0, 0, 0.



####
#### 3. Init Representation Contexts
####
#    (in this case a sphere if Representation Context is 3D ("Context Type = Model") 
#     and a circle with label if Representation Context is 2D ("Context Type = Plan"))
# a "Model" context.
model3d = run("context.add_context", model, context_type="Model")
# And/Or, if we plan to store 2D geometry, we need a "Plan" context
plan = run("context.add_context", model, context_type="Plan")
# Now we setup the subcontexts with each of the geometric "purposes"
# we plan to store in our model. "Body" is by far the most important
# and common context, as most IFC models are assumed to be viewable
# in 3D.
body = run("context.add_context", model,
    context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model3d)
# A 2D annotation subcontext for plan views are important for door
# swings, window cuts, and symbols for equipment like GPOs, fire
# extinguishers, and so on.
annotation = run("context.add_context", model,
    context_type="Plan", context_identifier="Annotation", target_view="PLAN_VIEW", parent=plan)

###
### 4. create geometry Representations at local placement
###
### https://blenderbim.org/docs-python/ifcopenshell-python/geometry_creation.html#mesh-representations
### Once you have an Object Placement and a Representation Context, you can now create a Representation.
# Each Representations must choose a geometry modeling technique.
# For example, you may specify a mesh-like geometry, which uses vertices, edges, and faces.
# Alternatively, you may specify 2D profiles extruded into solid shapes and potentially having boolean voids and subtractions.
# You may even specify single edges and linework without any surfaces or solids.
# Representations may even be single points, such as for survey points or structual point connections.
# After the Representation is created, you will need to assign the Representation to the IFC object (e.g. wall, door, slab, etc).
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
radius = 500.0
location = model.createIfcCartesianPoint((0.0, 0.0, 0.0))
axis = model.createIfcDirection((0.0, 0.0, radius)) # radius in millimeters
ref_direction = model.createIfcDirection((radius, 0.0, 0.0))
axis2placement3d = model.createIfcAxis2Placement3D(location, axis, ref_direction)
sphere = model.createIfcSphere(Radius=radius, Position=axis2placement3d)
sphere_representation = model.createIfcShapeRepresentation(ContextOfItems=body, RepresentationIdentifier="Body", RepresentationType="CSG", Items=[sphere])




###
### 5. Create an ifc element and then apply the local placement and the geometry Representation to this element
###
# Variante 2: if its all the same representation for all elements, asign the representation to the element type
# NOTE: this saves around 7000 lines of code at 1000 samples / 300 kBytes at 1000 samples
# element_type = run("root.create_entity", model, ifc_class="Ifcbuildingelementproxytype")
# run("geometry.assign_representation", model, product=element_type, representation=sphere_representation)

elements = []
placement_vectors = [(0,0,0), (3,5,2), (1,1,1)]
placement_vectors = placement_vectors = [(random.randint(0, 100), random.randint(0, 100), random.randint(0, 100)) for _ in range(1000)]
for placement_vector in placement_vectors:
    matrix = np.eye(4)
    matrix[:,3][0:3] = placement_vector
    representation = sphere_representation
    element = run("root.create_entity", model, ifc_class="Ifcbuildingelementproxy")
    elements.append(element)
    run("geometry.edit_object_placement", model, product=element, matrix=matrix, is_si=True)
    run("geometry.assign_representation", model, product=element, representation=sphere_representation)
    #Variante 2: or if its all the same representation for all elements:
    #run("type.assign_type", model, related_object=element, relating_type=element_type)

    ###
    ### 7b. simpler way to create a property set and add the properties to it
    ###
    pset = ifcopenshell.api.run("pset.add_pset", model, product=element, name="Probenahme PSET")
    ifcopenshell.api.run("pset.edit_pset", model, pset=pset, properties={"Testmethode": "Eimerprobe", "Entnahmetiefe": placement_vector[2], "Proben_Name": f"Probe {placement_vector[0]}-{placement_vector[1]}-{placement_vector[2]}"})


""" ALTERNATIVE (MANUAL) WAY TO CREATE A PROPERTY SET
###
### 6. Create a owner histroy from scratch
###
# Create an IfcPerson
person = model.createIfcPerson(None, "GivenName", "FamilyName", None, None, None, None, None)
# Create an IfcOrganization
organization = model.createIfcOrganization(None, "OrganizationName", None, None, None)
# Create an IfcPersonAndOrganization
person_and_organization = model.createIfcPersonAndOrganization(person, organization, None)
# Create an IfcApplication
application = model.createIfcApplication(organization, "ApplicationVersion", "ApplicationFullName", "ApplicationIdentifier")
# Create an IfcOwnerHistory
owner_history = model.createIfcOwnerHistory(person_and_organization, application, None, "ADDED", None, person_and_organization, application, int(time.time()))

###
### 7a. Create a property set and add the properties to it
###
# Create the properties
element = elements[0]
property_name1 = "Proben_Name"
property_value1 = model.createIfcText("Probe 1a")
single_property1 = model.createIfcPropertySingleValue(property_name1, None, property_value1, None)

property_name2 = "Proben_Entnahmetiefe"
property_value2 = model.createIfcReal(-1.0)
single_property2 = model.createIfcPropertySingleValue(property_name2, None, property_value2, None)

# Create a property set and add the properties to it
pset_name = "Probenahme"
properties = [single_property1, single_property2]
property_set = model.createIfcPropertySet(ifcopenshell.guid.new(), owner_history, pset_name, None, properties)
# Associate the property set with the element
rel_defines_by_properties = model.createIfcRelDefinesByProperties(ifcopenshell.guid.new(), owner_history, None, None, [element], property_set)
"""



###
### 7. Validate the model
###
from logging import getLogger
logger = getLogger("ifcopenshell")
ifcopenshell.validate.validate(model, logger)

###
### 8. Write the model to disk
###
model.write("./data/example4_output_model_var1.ifc")