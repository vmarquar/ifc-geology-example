import ifcopenshell
from ifcopenshell.api import run
import ifcopenshell.geom
import ifcopenshell.validate
import ifcopenshell.template
import ifcopenshell.util
import ifcopenshell.util.shape

import multiprocessing
import csv
import os.path

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

def create_flat_dict_from_pset_dict(pset_dict:dict[dict], element:ifcopenshell.entity_instance) -> dict:
    """
    This function creates a flat dictionary from a nested dictionary with the following structure:
        {PSET_NAME: {PROPERTY_NAME: PROPERTY_VALUE, ...}, ...}
        The PsetName will be the first part, then a dot, then the property name.
        e.g.: Pset_GeologicalUnit.Name, Pset_GeologicalUnit.Description
    Args:
        pset_dict (dict[dict]): a nested dictionary with the structure {PSET_NAME: {PROPERTY_NAME: PROPERTY_VALUE, ...}, ...}
        element (ifcopenshell.entity_instance): the element to which the was retrieved
    Returns:
        dict: a flat dictionary with the structure {"PSET_NAME.PROPERTY_NAME": "PROPERTY_VALUE", ...}
    """
    flat_dict_row = {'GlobalId':element.GlobalId,
                    'Name':element.Name}
    for key in pset_dict.keys():
        if(key in ['GlobalId', 'Name', 'Volume']):
            continue
        else:
            for prop in pset_dict[key].keys():
                if(prop != 'id'):
                    flat_dict_row[f'{key}.{prop}'] = None
    return flat_dict_row

def parse_pset_csv(file_path:str) -> (dict[dict], dict[dict], list[str]):
    """
    Parses a csv file with the following structure:
        GlobalId, PSET_NAME.PROPERTY_NAME, PSET_NAME.PROPERTY_NAME, ...
        e.g.: 3Fa99PJ5HBrvS$VA2PSulm, My first property,,1.23,My fourth property
    and returns a nested dictionary with the following structure:
        {GlobalId: {PSET_NAME: {PROPERTY_NAME: PROPERTY_VALUE, ...}, ...}, ...}
    the PsetName will be retrieved from the first part of the column name (i.e. before the first dot)

    Args:
        file_path (str): the path to the csv file
    Returns:
        dict: a nested dictionary with the structure {GlobalId: {PSET_NAME: {PROPERTY_NAME: PROPERTY_VALUE, ...}, ...}, ...}

    """
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        data = {}
        for row in reader:
            global_id = row['GlobalId']
            data[global_id] = {}
            for column, value in row.items():
                if column in ['GlobalId', 'Name', 'Volume'] or column[:3] == '.id':
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
    
        blank_structure = {}
        for field in reader.fieldnames:
            if(field in ['GlobalId', 'Name']):
                blank_structure[field] = None
            elif(field in ['id', 'Volume']):
                continue
            else:
                outer_key = field.split('.', 1)[0] # = pset name
                inner_key = field.split('.', 1)[1] # = property name
                if(outer_key not in blank_structure.keys()):
                    blank_structure[outer_key] = {}
                blank_structure[outer_key][inner_key] = None

    return data, blank_structure, reader.fieldnames

def add_suffix_to_file_path(file_path:str, suffix:str) -> str:
    base_name, ext = os.path.splitext(file_path)
    return f"{base_name}{suffix}{ext}"

