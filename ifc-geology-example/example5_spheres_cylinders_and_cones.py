import ezdxf
from ezdxf.render.forms import sweep, circle
from dataclasses import dataclass


@dataclass
class XYZPoint:
    x: float
    y: float
    z: float


@dataclass
class Borehole:
    hole_id: str
    drilling_radius: float
    drilling_path: list[XYZPoint]


def create_3d_as_built_borehole_cylinder_from_path(
    modelspace: ezdxf.document.Drawing.modelspace,
    borehole_path: list[XYZPoint],
    borehole_radius: float = 0.40,
    dxfattribs: dict = {"layer": "Borehole"},
):
    """
    This function creates a cylinder-like shape around a xyz-path.
    This function can be used to obtain an as-built drilling path.
    """
    # 1) Create a circle profile using ezdxf's circle function
    num_segments = 36  # Number of vertices to approximate the circle
    profile = list(
        circle(count=num_segments, radius=borehole_radius, elevation=0, close=True)
    )

    # 2) Sweep the profile along the path to generate a 3D mesh
    borehole_path = [(point.x, point.y, point.z) for point in borehole_path] # sweep() function takes immutable 3d vectors only!
    mesh = sweep(profile, borehole_path, close=True, quads=True, caps=True)

    # 3) Add the resulting mesh to the DXF modelspace
    mesh.render_mesh(modelspace, dxfattribs=dxfattribs)

    return mesh


def example5_main():
    """
    This example create a series of 3 drillings with differenz dip
    and saves them in one dxf file.
    """

    # 1) Create a new DXF document and add the modelspace
    doc = ezdxf.new("R2018")
    msp = doc.modelspace()

    # 2) Define sample data for three drillings
    drillings = [
        Borehole(
            hole_id="Drilling 1",
            drilling_path=[XYZPoint(0, 0, 0), XYZPoint(10, 0, -48)],
            drilling_radius=0.40,
        ),
        Borehole(
            hole_id="Drilling 2",
            drilling_path=[XYZPoint(0, 0, 0), XYZPoint(10, 0, -50)],
            drilling_radius=0.40,
        ),
        Borehole(
            hole_id="Drilling 3",
            drilling_path=[XYZPoint(0, 0, 0), XYZPoint(10, 0, -52)],
            drilling_radius=0.40,
        ),
    ]

    # 3) Iterate each drilling and create a 3d-mesh
    for drilling in drillings:
        create_3d_as_built_borehole_cylinder_from_path(
            modelspace=msp,
            borehole_path=drilling.drilling_path,
            borehole_radius=drilling.drilling_radius,
            dxfattribs={"layer": drilling.hole_id},
        )
    # 4) Save the DXF file
    doc.saveas(
        "/Users/valentin/Desktop/Share/01-5_dxfs/example5_drillinghole_as_built.dxf"
    )


if __name__ == "__main__":
    example5_main()
