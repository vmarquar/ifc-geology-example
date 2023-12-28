### IMPORTS
import ifcopenshell
from ifcopenshell.api import run
import ifcopenshell.geom
import ifcopenshell.validate
import ifcopenshell.util
import numpy as np

import random
from logging import getLogger

from ifc_utils.ifc_utils import init_minimal_ifc_model, create_sphere_representation, create_and_add_style

### CONSTANTS
EXPORT_FILENAME = "./data/example4_output_model_var2lean.ifc"
### FUNCTIONS

### MAIN
if __name__ == "__main__":

    # 1. Init project from default template
    model, project, site, body_3d_context, plan_2d_context = init_minimal_ifc_model(
        filename=EXPORT_FILENAME,
        organization="Faros",
        creator="Faros-Python-Script",
        project_name="Faros Example 4",
        create_3d_context=True,
        create_2d_context=True,
        add_site=True,
        site_name="Faros Example Site"
    )

    ### 2. create geometry Representations and styles
    style = create_and_add_style(model, red=0.25, green=1.0, blue=0.5, transparency=0.5)
    style_1500 = create_and_add_style(model, red=1.0, green=0.25, blue=0.5, transparency=0.5)
    sphere_representation = create_sphere_representation(model, representation_context=body_3d_context, radius=750.0)
    run("style.assign_representation_styles", model, shape_representation=sphere_representation, styles=[style])
    sphere_representation_1500 = create_sphere_representation(model, representation_context=body_3d_context, radius=1500.0)
    run("style.assign_representation_styles", model, shape_representation=sphere_representation_1500, styles=[style_1500])

    ### 2. create ifc element style categories (two in this case)
    element_type = run("root.create_entity", model, ifc_class="Ifcbuildingelementproxytype")  # Variante 2
    run("geometry.assign_representation", model,product=element_type,representation=sphere_representation)  # Variante 2 - Typ 1
    element_type_1500 = run("root.create_entity", model, ifc_class="Ifcbuildingelementproxytype")  # Variante 2
    run("geometry.assign_representation",model,product=element_type_1500,representation=sphere_representation_1500)  # Variante 2 - Typ 2

    ### 3. Create an ifc element and then apply the local placement and the geometry Representation to this element
    elements = []
    placement_vectors = placement_vectors = [
        (random.randint(0, 100), random.randint(0, 100), random.randint(0, 100))
        for _ in range(1000)
    ]
    for idx, placement_vector in enumerate(placement_vectors):
        matrix = np.eye(4)
        matrix[:, 3][0:3] = placement_vector
        representation = sphere_representation
        element = run("root.create_entity", model, ifc_class="IfcBuildingElementProxy")
        elements.append(element)
        run(
            "geometry.edit_object_placement",
            model,
            product=element,
            matrix=matrix,
            is_si=True,
        )
        # run("geometry.assign_representation", model, product=element, representation=sphere_representation) # Variante 1 (Use this if you have continous data without clusters/bins/categories)
        if idx % 2 == 0:
            run( "type.assign_type", model, related_object=element, relating_type=element_type)  # Variante 2 - Typ 1 (Example for even numbers)
        else:
            run( "type.assign_type", model, related_object=element, relating_type=element_type_1500)  # Variante 2 - Typ 2 (Example for odd numbers)

        ### 4. simpler way to create a property set and add the properties to it
        pset = run("pset.add_pset", model, product=element, name="Probenahme PSET")
        run("pset.edit_pset",
            model,
            pset=pset,
            properties={
                "Testmethode": "Eimerprobe",
                "Entnahmetiefe": placement_vector[2],
                "Proben_Name": f"Probe {placement_vector[0]}-{placement_vector[1]}-{placement_vector[2]}",
            },
        )

    ### 5. Validate the model
    logger = getLogger("ifcopenshell")
    ifcopenshell.validate.validate(model, logger)

    ### 6. Write the model to disk
    model.write(EXPORT_FILENAME)