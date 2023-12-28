import ifcopenshell
from ifcopenshell.api import run
import ifcopenshell.geom
import ifcopenshell.validate
import ifcopenshell.template
import ifcopenshell.util
import ifcopenshell.util.shape

import multiprocessing
import csv

def get_application(file: ifcopenshell.file, verbose:bool=False) -> dict | None:
    try:
        application = file.by_type('IFCAPPLICATION')[0]
        application_info = application.get_info()
        return application_info
    except Exception as e:
        if (verbose):
            print(f"Error: {e}")
        return None
    
def add_pset_with_props(model: ifcopenshell.file(), element: ifcopenshell.entity_instance, pset_name:str, properties:dict):
    """
    Description:
        Adds a PSET with a given name and properties to the given element
    Input:
        model: ifcopenshell.file()
        element: ifcopenshell.entity_instance
        pset_name: str
        properties: dict, e.g. {"Name": "Probenahme", "Description": "Probenahme", "Testmethode": "Eimerprobe", "Entnahmetiefe": 0.0, "Proben_Name": "Probe 1"}
    Output:
        pset: ifcopenshell.entity_instance
    """
    pset = run("pset.add_pset", model, product=element, name=pset_name)
    run("pset.edit_pset",
        model,
        pset=pset,
        properties=properties,
    )
    return pset

def init_minimal_ifc_model(
    filename: str | None = None,
    organization: str | None = None,
    creator: str | None = None,
    project_name: str | None = None,
    create_3d_context: bool = True,
    create_2d_context: bool = False,
    add_site: bool = False,
    site_name: str | None = None,
):
    """
    Description:
        Creates a minimal ifc model with a project and returns the model.
        - creates a ifc4 Project
        - creates all metric units and degrees as angle unit
        - creates a 3D and 2D representation context (3D by default, 2D optional)
    Input:
        filename: str | None
        organization: str | None
        creator: str | None
        project_name: str | None
    Output:
        model: ifcopenshell.file()
    https://stackoverflow.com/questions/51665572/required-data-for-ifc
    """
    ### 1. Init the Model, Units and create a Project (mandatory)
    model = ifcopenshell.template.create(
        filename=filename,  # '' will be used if None
        organization=organization,  # no ifc-entity will be created if None
        creator=creator,  # no ifc-entity will be created if None
        schema_identifier="IFC4",  # 'IFC4' will be used if None
        application_version=None,  # ifcopenshell will be used if None
        timestamp=None,  # now() will be used if None
        application=None,  # ifcopenshell will be used if None
        project_globalid=None,  # a random uuid will be used if None
        project_name=project_name, # '' will be used if None
    )
    project = model.by_type("IfcProject")[0]
    # Alternatively specify project and units manually
    # model = ifcopenshell.file()
    # project = run("root.create_entity", model, ifc_class="IfcProject", name=project_name)
    # length = ifcopenshell.api.run("unit.add_si_unit", model, unit_type="LENGTHUNIT")
    # area = ifcopenshell.api.run("unit.add_si_unit", model, unit_type="AREAUNIT")
    # angle = ifcopenshell.api.run("unit.add_si_unit", model, unit_type="PLANEANGLEUNIT")
    # ifcopenshell.api.run("unit.assign_unit", model, units=[length, area, angle])

    ### 2. Add Representation Context for 2D (Plan) and 3D (Model)
    if(create_3d_context):    
        model3d = run("context.add_context", model, context_type="Model")
        body_3d_context = run(
            "context.add_context",
            model,
            context_type="Model",
            context_identifier="Body",
            target_view="MODEL_VIEW",
            parent=model3d,
        )
    else:
        model3d, body_3d_context = None, None

    if(create_2d_context):
        plan = run("context.add_context", model, context_type="Plan")
        plan_2d_context = run(
            "context.add_context",
            model,
            context_type="Plan",
            context_identifier="Annotation",
            target_view="PLAN_VIEW",
            parent=plan,
        )
    else:
        plan, plan_2d_context = None, None

    if(add_site):
        # The project contains a site (note that project aggregation is a special case in IFC)
        site = run("root.create_entity", model, ifc_class="IfcSite", name=site_name)
        run("aggregate.assign_object", model, product=site, relating_object=project)
    else:
        site = None

    return model, project, site, body_3d_context, plan_2d_context


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

    # A profile-based representation, 1 meter long
    semiarc_representation = builder.get_representation(context=body, items=semiarc_extrusion)
    arbitrary_representation = run("geometry.add_profile_representation", model, context=body, profile=arbitrary_profile, depth=1.0) # creates a arbitrary_profile with 1m height 
    semicircle_representation = run("geometry.add_profile_representation", model, context=body, profile=semicircle_profile, depth=1.0) # creates a arbitrary_profile with 1m height 
    swept_rebar_representation = builder.get_representation(body, swept_rebar_curve)

    vertices = [[(0.,0.,0.), (0.,2.,0.), (2.,2.,0.), (2.,0.,0.), (1.,1.,1.)]]
    faces = [[(0,1,2,3), (0,4,1), (1,4,2), (2,4,3), (3,4,0)]]
    pyramide_representation = run("geometry.add_mesh_representation", model, context=body, vertices=vertices, faces=faces)
"""

def create_cylinder_representation(
    model: ifcopenshell.file(),
    representation_context: ifcopenshell.entity_instance,
    cylinder_height: float = 1000.0, #TODO: check if always in mm or project dependent
    cylinder_radius: float = 500.0, #TODO: check if always in mm or project dependent
    profile_name: str|None = None,
):
    """
    Description:
        Creates a cylinder representation with a given height and radius and adds it to the given representation_context
    Input:
        model: ifcopenshell.file()
        representation_context: ifcopenshell.entity_instance (e.g. body) body.is_a() == 'IfcGeometricRepresentationSubContext'
        cylinder_height: float
        cylinder_radius: float
    Output:
        cylinder_representation: ifcopenshell.entity_instance
    """
    profile = model.create_entity("IfcCircleProfileDef", ProfileName=profile_name, ProfileType="AREA", Radius=cylinder_radius)
    cylinder_representation = run("geometry.add_profile_representation", model, context=representation_context, profile=profile, depth=cylinder_height) 
    return cylinder_representation

def create_sphere_representation(
    model: ifcopenshell.file(),
    representation_context: ifcopenshell.entity_instance,
    radius: float = 500.0,
):
    """
    Description:
        Creates a sphere representation with a given radius and adds it to the given representation_context
    Input:
        model: ifcopenshell.file()
        representation_context: ifcopenshell.entity_instance (e.g. body) body.is_a() == 'IfcGeometricRepresentationSubContext'
        radius: float
    Output:
        sphere_representation: ifcopenshell.entity_instance
    """
    # new try - https://blenderbim.org/docs-python/ifcopenshell-python/geometry_creation.html#extruded-area-solid
    location = model.createIfcCartesianPoint((0.0, 0.0, 0.0))
    axis = model.createIfcDirection((0.0, 0.0, radius))  # radius in millimeters
    ref_direction = model.createIfcDirection((radius, 0.0, 0.0))
    axis2placement3d = model.createIfcAxis2Placement3D(location, axis, ref_direction)
    sphere = model.createIfcSphere(Radius=radius, Position=axis2placement3d)
    sphere_representation = model.createIfcShapeRepresentation(
        ContextOfItems=representation_context,
        RepresentationIdentifier="Body",
        RepresentationType="CSG",
        Items=[sphere],
    )
    return sphere_representation


def create_and_add_style(
    model: ifcopenshell.file(),
    red: float = 1.0,
    green: float = 0.5,
    blue: float = 0.5,
    transparency: float = 0.5,
):
    """
    Description:
        Creates a style with a given RGB and transparency value and adds it to the model
        Additional info can be found at https://blenderbim.org/docs-python/autoapi/ifcopenshell/api/style/assign_representation_styles/index.html?highlight=style#module-ifcopenshell.api.style.assign_representation_styles
        The Output style can be applied to a representation with 'ifcopenshell.api.run("style.assign_representation_styles", model, shape_representation=representation, styles=[style])'
    Input:
        model: ifcopenshell.file()
        red: float
        green: float
        blue: float
        transparency: float
    Output:
        style: ifcopenshell.entity_instance
    """

    # 1) Validate Input:
    if not (
        0.0 <= red <= 1.0
        and 0.0 <= green <= 1.0
        and 0.0 <= blue <= 1.0
        and 0.0 <= transparency <= 1.0
    ):
        raise ValueError("RGB+Transparency values must be between 0 and 1")

    # 2) Create a new surface style (a very simple one)
    style = ifcopenshell.api.run("style.add_style", model)
    ifcopenshell.api.run(
        "style.add_surface_style",
        model,
        style=style,
        ifc_class="IfcSurfaceStyleShading",
        attributes={
            "SurfaceColour": {
                "Name": None,
                "Red": red,
                "Green": green,
                "Blue": blue,
            },  # RGB values between 0 and 1
            "Transparency": transparency,  # 0 is opaque, 1 is transparent
        },
    )
    return style

def calc_volumes(ifc_file:ifcopenshell.file, use_world_coords:bool=True) -> dict:
    """
    Calculates the volumes of all entities in the IFC file
    Args:
        ifc_file (ifcopenshell.file): IFC file
    Returns:
        dict: dictionary with the volumes of all entities, 
            e.g. {'2HBKPyXqbEBOFvEOPaWIoH': 
                    {'volume': 0.0, 'name': 'Unit 1 - Clay'},
                '2HBKPyXqbEBOFv12123IoH': 
                    {'volume': 0.0, 'name': 'Unit 2 - Sand'}, 
                ...}
    """
    entities_with_volumes = {}
    settings = ifcopenshell.geom.settings()
    if(use_world_coords):
        settings.set(settings.USE_WORLD_COORDS, True)

    iterator = ifcopenshell.geom.iterator(settings, ifc_file, multiprocessing.cpu_count())
    if iterator.initialize():
        while True:
            try:    
                shape = iterator.get()
                
                if(shape is not None):
                    volume = ifcopenshell.util.shape.get_volume(shape.geometry)
                    volume_info = {
                        'volume':volume,
                        'name':shape.name
                    }
                    entities_with_volumes[shape.guid] = volume_info # can be a dict, as the guid is unique
            except Exception as e:
                print(f"Error: {e}")
                pass
            if not iterator.next():
                break
    return entities_with_volumes

def write_list_of_dict_to_csv(data: list[dict], filepath:str, round_floats:bool=True) -> str:
    ROUND_DECIMALS = 4
    keys = data[0].keys() if data else []
    
    if(round_floats):
        data = [{key: round(value, ROUND_DECIMALS) if isinstance(value, (int, float)) else value for key, value in item.items()} for item in data]
    
    with open(filepath, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)
    
    return(filepath)