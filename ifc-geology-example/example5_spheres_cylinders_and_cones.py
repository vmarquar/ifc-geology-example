import ezdxf
from ezdxf.render.forms import sweep, circle
from dataclasses import dataclass
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

@dataclass
class XYZPoint:
    """ Represents a point in 3D space. """
    x: float
    y: float
    z: float

@dataclass
class Borehole:
    """ Represents a borehole with a unique ID, drilling radius, and drilling path. """
    hole_id: str
    drilling_radius: float
    drilling_path: list[XYZPoint]

def validate_borehole_data(borehole: Borehole) -> None:
    """ Validates the borehole data.
    Args:
        borehole (Borehole): The borehole instance to validate.
    Raises:
        ValueError: If the borehole data is invalid.
    """
    if borehole.drilling_radius <= 0:
        raise ValueError(f"Borehole radius must be positive: {borehole.drilling_radius}")
    
    if len(borehole.drilling_path) < 2:
        raise ValueError("The Drilling path must contain at least two points!")

def create_borehole_cylinder(
    modelspace: ezdxf.document.Drawing.modelspace,
    borehole_path: list[XYZPoint],
    borehole_radius: float = 0.40,
    num_segments: int = 36,
    dxfattribs: dict = {"layer": "Borehole"},
) -> ezdxf.render.MeshTransformer:
    """ Creates a 3D cylinder representation of a borehole based on its drilling path.
    Args:
        modelspace (ezdxf.document.Drawing.modelspace): The DXF modelspace where the cylinder will be added.
        borehole_path (list[XYZPoint]): A list of XYZPoint instances representing the drilling path.
        borehole_radius (float, optional): The radius of the borehole in meters. Defaults to 0.40.
        num_segments (int, optional): The number of segments used to approximate the circular profile. Defaults to 36.
        dxfattribs (dict, optional): Attributes for the DXF entities, such as layer information. Defaults to {"layer": "Borehole"}.
    Raises:
        ValueError: If the provided borehole data is invalid.
    Returns:
        None: This function does not return a value; it modifies the modelspace directly.
    """
    
    # 1) Create a circle profile
    profile = list(circle(count=num_segments, radius=borehole_radius, elevation=0, close=True))
    
    # 2) Sweep the profile along the path to generate a 3D mesh
    borehole_path = [(point.x, point.y, point.z) for point in borehole_path]  # Convert to immutable vectors
    mesh = sweep(profile, borehole_path, close=True, quads=True, caps=True)
    
    # 3) Add the resulting mesh to the DXF modelspace
    mesh.render_mesh(modelspace, dxfattribs=dxfattribs)
    logging.info(f"Borehole cylinder created for {dxfattribs['layer']}")
    
    return(mesh)

def example5_main():
    """Main function to create and save a series of boreholes in a DXF file.

    This function initializes a new DXF document, defines sample drilling data for three boreholes,
    generates 3D meshes for each borehole, and saves the resulting DXF file.

    Returns:
        None: This function does not return a value.
    """
    # 1) Create a new DXF document
    doc = ezdxf.new("R2018")
    msp = doc.modelspace()

    # 2) Define sample data for three drillings
    drillings = [
        Borehole(hole_id="Drilling 1", drilling_path=[XYZPoint(0, 0, 0), XYZPoint(10, 0, -48)], drilling_radius=0.40),
        Borehole(hole_id="Drilling 2", drilling_path=[XYZPoint(0, 0, 0), XYZPoint(10, 0, -50)], drilling_radius=0.40),
        Borehole(hole_id="Drilling 3", drilling_path=[XYZPoint(0, 0, 0), XYZPoint(10, 0, -52)], drilling_radius=0.40),
        Borehole(hole_id="Drilling 4 with Errors", drilling_path=[XYZPoint(0, 0, 0), XYZPoint(10, 0, -52)], drilling_radius=-0.40),
        Borehole(hole_id="Drilling 5 with Errors", drilling_path=[XYZPoint(0, 0, 0)], drilling_radius=0.40),
    ]

    # 3) Validate each drilling and create 3D meshes
    for drilling in drillings:
        try:
            validate_borehole_data(drilling)  # Validate the borehole data
            create_borehole_cylinder(
                modelspace=msp,
                borehole_path=drilling.drilling_path,
                borehole_radius=drilling.drilling_radius,
                dxfattribs={"layer": drilling.hole_id},
            )
        except ValueError as e:
            logging.error(f"Error with {drilling.hole_id}: {e}")

    # 4) Save the DXF file
    save_path = "/Users/valentin/Desktop/Share/01-5_dxfs/example5_drillinghole_as_built.dxf"
    doc.saveas(save_path)
    logging.info(f"DXF file saved at: {save_path}")

if __name__ == "__main__":
    example5_main()
