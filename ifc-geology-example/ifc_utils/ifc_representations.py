import ifcopenshell
from ifcopenshell.api import run

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
    style = run("style.add_style", model)
    run(
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
