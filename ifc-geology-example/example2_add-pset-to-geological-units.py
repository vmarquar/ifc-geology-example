### IMPORTS
import ifcopenshell
import ifcopenshell.geom 

import os.path
from logging import getLogger

from ifc_utils.ifc_utils import add_pset_with_props, get_application, calc_volumes, write_list_of_dict_to_csv, add_suffix_to_file_path, parse_pset_csv, create_flat_dict_from_pset_dict

### CONSTANTS
COMPUTE_VOLUME = False
MISSING_ROWS_FILEPATH =  "./data/leapfrog_examples/geological_units_psets.csv"
EXAMPLE_PSET_STRUCTURE = {
            "Pset_GeologicalUnit": {
                "Name": "Geological Unit 2",
                "Description": "This is the second geological unit",
                "Homogenous Area": "B2 - Clay"
            },
            "Pset_CharacteristicValues": {
                "friction angle, characteristic [°]": 27.5,
                "friction angle, min [°]": 25.0,
                "friction angle, max [°]": 27.5
            },
        }


### FUNCTIONS
def main(ifc_file_path:str):
    """
    Adds the Psets to all geological units in the IFC file, if a csv file is provided.
    Otherwise it creates a csv file with the current globalIds and Names of the geological units, 
    that can be used to import the psets and properties on a second run of this script.
    
    The script assumes that the geological units are IfcBuildingElementProxy.
    """

    rows = []
    pset_blank_structure = None
    add_psets_nested_dict = None
    if(os.path.isfile(MISSING_ROWS_FILEPATH)):
        add_psets_nested_dict, pset_blank_structure, csv_fieldnames = parse_pset_csv(MISSING_ROWS_FILEPATH)
    else:
        add_psets_nested_dict = None
        pset_blank_structure = EXAMPLE_PSET_STRUCTURE

    model = ifcopenshell.open(ifc_file_path)

    # 1. Check if its a Leapfrog Works generated IFC file
    app_info = get_application(model)
    if(app_info['ApplicationFullName'] != 'Leapfrog Works'): # currently tested on 2022.1.1, add your version number to test another version of LF Works
        print(f"Error: Application is not Leapfrog Works. Application is: {get_application(model)}")
        exit()

    # 2. Compute all the volumes of all entities in the model
    volumes = {}
    if(COMPUTE_VOLUME):
        print("Warning: Retrieving volumes is a computational intensive operation and can take some time (~30 seconds per unit)")
        volumes = calc_volumes(model)

    # 3. Select the geological units
    # IFC4: assuming that the geological units are IfcBuildingElementProxy
    geological_units = model.by_type('IfcBuildingElementProxy') 

    # 4. Add the Pset_GeologicalUnit to each geological unit
    for geological_unit in geological_units:

        volume = volumes.get(geological_unit.GlobalId)['volume'] if (COMPUTE_VOLUME == True) else None

        try:    
            psets = add_psets_nested_dict[geological_unit.GlobalId].keys()
            for pset_name in psets:
                props = add_psets_nested_dict[geological_unit.GlobalId][pset_name]

                pset_element = add_pset_with_props(model, geological_unit, pset_name, props)
                added_psets = ifcopenshell.util.element.get_psets(geological_unit)
                # will update existing psets and props
                existing_row = create_flat_dict_from_pset_dict(pset_dict=added_psets, element=geological_unit)
                if(COMPUTE_VOLUME):
                    existing_row['Volume'] = volume
                rows.append(existing_row)
                print(f"Pset added/updated to Name: '{geological_unit.Name}'\nID: '{geological_unit.GlobalId}'\nVolume [m3]: {f'{volume:.2e}' if volume is not None else 'N/A'}\n")

        except (KeyError, TypeError) as error:
            print(f"Error: No Pset found for '{geological_unit.GlobalId}' with name '{geological_unit.Name}'\n")
            missing_row = create_flat_dict_from_pset_dict(pset_dict=pset_blank_structure, element=geological_unit)
            if(COMPUTE_VOLUME):
                missing_row['Volume'] = volume
            rows.append(missing_row)

    # 5. Write the missing rows to a csv file
    if(len(rows)>0):
        outpath = write_list_of_dict_to_csv(rows, MISSING_ROWS_FILEPATH)
        print(f"A csv file for all geological units (i.e. IfcBuildingElementProxy) has been written to: {outpath}")
        print("You can use this file to add or modify psets to the geological units in the IFC file.\nEdit the csv file and run this script again to add the missing psets to the geological units to the IFC file.\n")

    # 6. Validate the model
    logger = getLogger("ifcopenshell")
    ifcopenshell.validate.validate(model, logger)

    # 7. Save the model
    new_filepath = add_suffix_to_file_path(ifc_file_path, "_with_psets")
    model.write(new_filepath)
    print("The updated IFC FIle has been written to: ", new_filepath)

### MAIN
if __name__ == "__main__":
    main(ifc_file_path="./data/leapfrog_examples/Geological_units_10+250_10+700_with_psets.ifczip")