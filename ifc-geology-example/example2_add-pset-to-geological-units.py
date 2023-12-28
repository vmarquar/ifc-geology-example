### IMPORTS
import ifcopenshell
import ifcopenshell.geom 
from ifc_utils.ifc_utils import add_pset_with_props, get_application, calc_volumes, write_list_of_dict_to_csv
import csv
import os.path

### CONSTANTS
COMPUTE_VOLUME = False
MISSING_ROWS_FILEPATH =  "./data/leapfrog_examples/missing_psets.csv"

EXAMPLE_PSETS_AND_PROPS_TO_ADD = {
    "3Fa99PJ5HBrvS$VA2PSulm": {
        "Pset_GeologicalUnit": {
            "Name": "Geological Unit 1",
            "Description": "This is the first geological unit",
            "Homogenous Area": "B1 - Sand",
            "friction angle, characteristic [°]": 30.0,
            "friction angle, min [°]": 27.5,
            "friction angle, max [°]": 32.5
        }
    },
    "3IPaY$O7f1RwLaO2ojkyDI": {
        "Pset_GeologicalUnit": {
            "Name": "Geological Unit 2",
            "Description": "This is the second geological unit",
            "Homogenous Area": "B2 - Clay",
            "friction angle, characteristic [°]": 27.5,
            "friction angle, min [°]": 25.0,
            "friction angle, max [°]": 27.5
        }
    },
}

### FUNCTIONS
def parse_csv(file_path:str) -> dict[dict]:
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        data = {}
        for row in reader:
            global_id = row['GlobalId']
            data[global_id] = {}
            for column, value in row.items():
                if column == 'GlobalId':
                    continue
                parts = column.split('.')
                outer_key = parts[0]
                inner_key = '.'.join(parts[1:])
                if outer_key not in data[global_id]:
                    data[global_id][outer_key] = {}
                if value == '':
                    data[global_id][outer_key][inner_key] = None
                else:
                    data[global_id][outer_key][inner_key] = float(value) if value and value.replace('.', '', 1).isdigit() else value
    return data

def add_suffix_to_file_path(file_path:str, suffix:str) -> str:
    base_name, ext = os.path.splitext(file_path)
    return f"{base_name}{suffix}{ext}"

def main(ifc_file_path:str="./data/leapfrog_examples/Geological_units_10+250_10+700.ifczip"):
    missing_rows = []
    add_psets_nested_dict = None
    if(os.path.isfile(MISSING_ROWS_FILEPATH)):
        add_psets_nested_dict = parse_csv(MISSING_ROWS_FILEPATH)
    else:
        add_psets_nested_dict = EXAMPLE_PSETS_AND_PROPS_TO_ADD

    model = ifcopenshell.open(ifc_file_path)

    # 1. Check if its a Leapfrog Works generated IFC file
    app_info = get_application(model)
    if(app_info['ApplicationFullName'] != 'Leapfrog Works'): # currently tested on 2022.1.1, add your version number to test another version of LF Works
        print(f"Error: Application is not Leapfrog Works. Application is: {get_application(model)}")
        exit()

    # 2. Compute all the volumes of all entities in the model
    volumes = {}
    if(COMPUTE_VOLUME):
        print("Warning: This is a computational intensive operation and can take some time (~30 seconds per unit)")
        volumes = calc_volumes(model)

    # 3. Select the geological units
    # IFC4: assuming that the geological units are IfcBuildingElementProxy
    geological_units = model.by_type('IfcBuildingElementProxy') 

    # 4. Add the Pset_GeologicalUnit to each geological unit
    for geological_unit in geological_units:

        volume = volumes.get(geological_unit.GlobalId)['volume'] if COMPUTE_VOLUME else None

        try:    
            psets = add_psets_nested_dict[geological_unit.GlobalId].keys()
            for pset_name in psets:
                props = add_psets_nested_dict[geological_unit.GlobalId][pset_name]
                if(COMPUTE_VOLUME):
                    props['Volume [m3]'] = volume

                pset_element = add_pset_with_props(model, geological_unit, pset_name, props)
                added_psets = ifcopenshell.util.element.get_psets(geological_unit)
                #TODO: check if the pset was added correctly, add it to completed_rows
                print(f"Pset added to Name: '{geological_unit.Name}'\nID: '{geological_unit.GlobalId}'\nVolume [m3]: {f'{volume:.2e}' if volume is not None else 'N/A'}\n")

        except KeyError:
            print(f"Error: No Pset found for '{geological_unit.GlobalId}' with name '{geological_unit.Name}'\n")
            missing_row = {'GlobalId':geological_unit.GlobalId,
                'Pset_GeologicalUnit.Name':geological_unit.Name,
                'Pset_GeologicalUnit.Description':None,
                'Pset_GeologicalUnit.Homogenous Area':None,
                'Pset_GeologicalUnit.friction angle, characteristic [°]':None,
                'Pset_GeologicalUnit.friction angle, min [°]':None,
                'Pset_GeologicalUnit.friction angle, max [°]':None,
                'Pset_GeologicalUnit.Volume [m3]':volume}
            missing_rows.append(missing_row)

    # 5. Write the missing rows to a csv file
    if(len(missing_rows)>0):
        
        outpath = write_list_of_dict_to_csv(missing_rows, MISSING_ROWS_FILEPATH)
        print(f"A csv file with the missing psets for all geological units (i.e. IfcBuildingElementProxy) has been written to: {outpath}")
        print("You can use this file to add the missing psets to the geological units in the IFC file.\nRun this script again to add the missing psets to the geological units in the IFC file.\n")

    # TODO: write the completed rows to a csv file

    # 6. Save the model
    model.write(add_suffix_to_file_path(ifc_file_path, "_with_psets"))
### MAIN
if __name__ == "__main__":
    main()