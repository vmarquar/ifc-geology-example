# IFC & Leapfrog & Geological Modelling examples

### Examples
`ifc-geology-example/example1_parse-leapfrog-boreholes-to-csv.py` shows how to parse an ifc file created from Leapfrog Works. It will extract all boreholes and their intervals into 2 csv files.

`ifc-geology-example/example2_add-pset-to-geological-units.py` shows how to retrieve all geological units / volume bodies and shows how to add PSETs and Properties to the geological units using a csv helper file. Additionally it can compute the volume of all geological bodies.

`ifc-geology-example/example3_create-spheres.py` shows how to create an ifc file from scratch and create random spheres and attach a pset and properties to each of them.

### Useful links
- https://www.youtube.com/watch?v=RjG_AFiTedE
- https://blenderbim.org/docs-python/introduction/introduction_to_ifc.html
- https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/annex-c.html
- https://blenderbim.org/docs-python/ifcopenshell-python/geometry_creation.html


### Installation
`pip install ifcopenshell` or `poetry add ifcopenshell` or after downloading from git `poetry install` or `poetry install --no-root`
