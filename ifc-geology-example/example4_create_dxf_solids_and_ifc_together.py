### IMPORTS
from ifc_utils.ifc_utils import get_application, write_list_of_dict_to_csv
import csv, math
from typing import List, Tuple, Iterable

import ezdxf
from ezdxf.render.forms import cube, cylinder_2p, cone_2p, cone, sweep, circle, from_profiles_linear
from ezdxf.addons.pycsg import CSG

### CONSTANTS

### FUNCTIONS
def read_csv(file_path: str, decimal_separator: str = ".") -> list:
    """
    Reads a CSV file and converts the data into numerics where possible.
    """
    def is_numeric(input_string: str) -> bool:
        try:
            float(input_string.replace(decimal_separator, '.'))
            return True
        except ValueError:
            return False

    def convert_to_numeric(x: str) -> float:
        return float(x) if is_numeric(x) else x

    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile, quotechar='"')
        data = []
        for row in reader:
            row_with_numerics = {key: convert_to_numeric(value) for key, value in row.items()}
            data.append(row_with_numerics)
    return data


def tolerance_body_as_mesh(start: Tuple[float, float, float], end: Tuple[float, float, float], start_radius:float = 0.05, tolerance_factor:float = 0.02):

    # 1) calculate the needed distances and values for the geometry generation
    
    maximum_length = math.sqrt( (end[0]-start[0])**2  + (end[1]-start[1])**2 + (end[2]-start[2])**2)
    end_radius = start_radius + (maximum_length*tolerance_factor)
    dip = 0
    azimuth = 0

    # 2) construct the tolarance body along the z-axis, oriented upwards
    starting_circle = circle(count=32, radius=start_radius, elevation=0.0, close=False)
    end_circle = circle(count=32, radius=end_radius, elevation=maximum_length, close=False)
    tolerance_body_mesh = from_profiles_linear([starting_circle, end_circle])

    # 3) Translate and Transpose the tolerance body to match its final destination in the WCS
    tolerance_body_mesh.translate(dx=start[0], dy=start[1], dz=start[2]) # um 10 RAD gedreht

    # TODO: Bringe den Toleranzkörper in die Echte Welt
    # Drehung gehen Nord = Azimuth
    # drehung gegen die Z-Achse = dip
    # Verschiebung auf Ansatzpunkt 


    return(tolerance_body_mesh)


### MAIN
if __name__ == "__main__":

    ### BEISPIEL 2
    planned_drillings = read_csv('./data/planned_drillings.csv')



    ### BEISPIEL 1

    

    # create new DXF document
    doc = ezdxf.new()
    doc.units = ezdxf.units.M
    msp = doc.modelspace()


    # create same geometric primitives as MeshTransformer() objects
    cone1 = cone()
    cone1.render_mesh(msp, dxfattribs={'color': 2, "layer": "tolerance_bodies"})
    cone1.translate(20)


    ### construct a conical frustum / Kegelstumpf
    cube1 = cube()
    cylinder1 = cylinder_2p(count=32, base_center=(0, -1, 0), top_center=(0, 1, 0), radius=.25)

    # build solid union
    union = CSG(cube1) + CSG(cylinder1)
    # convert to mesh and render mesh to modelspace
    union.mesh().render_mesh(msp, dxfattribs={'color': 1})

    # build solid difference
    difference = CSG(cube1) - CSG(cylinder1)
    # convert to mesh, translate mesh and render mesh to modelspace
    difference.mesh().translate(1.5).render_mesh(msp, dxfattribs={'color': 3})

    # build solid intersection
    intersection = CSG(cube1) * CSG(cylinder1)
    # convert to mesh, translate mesh and render mesh to modelspace
    intersection.mesh().translate(2.75).render_mesh(msp, dxfattribs={'color': 5})


    

    # #doc.saveas('./data/csg_primitive.dxf')

    # # Define parameters for the conical frustum
    # top_radius = 0.05  # 5 centimeters
    # height = 10  # 10 meters
    # tolerance_factor = 0.02  # tolerance per meter depth/length
    # bottom_radius = tolerance_factor * height + top_radius

    
    # # Define the profile of the frustum as a list of vertices
    # profile = [
    #     (top_radius, 0),            # Top vertex
    #     (bottom_radius, -height),    # Bottom vertex
    # ]

    # # Create the conical frustum by rotating the profile around the z-axis
    # count = 50  # Number of rotated profiles
    # angle = math.tau  # Full rotation (360 degrees)
    # axis = (0, 0, 1)  # z-axis

    # # Use rotation_form to create the conical frustum
    # frustum_transformer = ezdxf.render.forms.rotation_form(count, profile, angle, axis)

    # # Apply the transformation to create the conical frustum as a mesh

    # # Add the conical frustum mesh to the modelspace
    # frustum_transformer.translate(10).render_mesh(msp, dxfattribs={'color': 5})



    ###### EXAMPLE 21.05.2024 - SWEEP
    base_circle_profile = circle(count=32, radius=2, elevation=0.0, close=False)
    path = [(10,10,0), (20,20,10), (25,25,15)]
    sweeped_mesh_transformer = sweep(profile=base_circle_profile, sweeping_path=path, close=True, quads=True, caps=True)
    sweeped_mesh_transformer.translate(dx=5,dy=5,dz=10).render_mesh(msp, dxfattribs={'color': 8})

    ###### EXAMPLE 2 - Tolerance Body
    tolerance_body = tolerance_body_as_mesh(start=(0,0,0), end=(15,15,15), start_radius=0.05, tolerance_factor=0.02)
    tolerance_body.render_mesh(msp, dxfattribs={'color': 2, "layer": "tolerance_bodies"})

    tolerance_body2 = tolerance_body_as_mesh(start=(-15,-15,0), end=(10,20,30), start_radius=0.05, tolerance_factor=0.02)
    tolerance_body2.render_mesh(msp, dxfattribs={'color': 2, "layer": "tolerance_bodies"})







    # Save the DXF file
    doc.saveas("./data/cylinders_and_sweeps.dxf")

    pass