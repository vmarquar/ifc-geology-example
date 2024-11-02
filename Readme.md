# IFC & Leapfrog & Geological Modelling examples

### Dependencies

- `numpy`
- `ifcopenshell` for Examples 01, 02 & 03
- `ezdxf` for Examples 04, 05 & 07
- `wellpathpy` for Example 07

### Examples

-  `ifc-geology-example/example1_parse-leapfrog-boreholes-to-csv.py` shows how to parse an ifc file created from Leapfrog Works. It will extract all boreholes and their intervals into 2 csv files.

- `ifc-geology-example/example2_add-pset-to-geological-units.py` shows how to retrieve all geological units / volume bodies and shows how to add PSETs and Properties to the geological units using a csv helper file. Additionally it can compute the volume of all geological bodies.

- `ifc-geology-example/example3_create-spheres.py` shows how to create an ifc file from scratch and create random spheres and attach a pset and properties to each of them.

- `example3_create-spheres.py` creates a series of spheres and attaches some example pset to them. The shapes are exported to an ifc file.

- `example4_create_dxf_solids_and_ifc_together.py` WIP

- `example5_spheres_cylinders_and_cones.py`

- `example7_sperical_arc_approximation.py`

### Useful links
- https://www.youtube.com/watch?v=RjG_AFiTedE
- https://blenderbim.org/docs-python/introduction/introduction_to_ifc.html
- https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/annex-c.html
- https://blenderbim.org/docs-python/ifcopenshell-python/geometry_creation.html


### Installation
`pip install ifcopenshell` or `poetry add ifcopenshell` or after downloading from git `poetry install` or `poetry install --no-root`
