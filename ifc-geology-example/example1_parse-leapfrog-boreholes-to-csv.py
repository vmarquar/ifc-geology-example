# conda activate gis_env
# conda install -c conda-forge ifcopenshell # if this does not work install via pip install ifcopenshell
import numpy as np
import ifcopenshell
import ifcopenshell.util.element as element
import ifcopenshell.geom
import ifcopenshell.util.shape
import time

from ifc_utils.ifc_utils import get_application, write_list_of_dict_to_csv

def get_bbox_test(elem: ifcopenshell.entity_instance, use_world_coords:bool=True, verbose:bool=False) -> dict:
    # shape.bounds does not work 
    try:
        settings = ifcopenshell.geom.settings()
        if(use_world_coords):
            settings.set(settings.USE_WORLD_COORDS, True)
        shape = ifcopenshell.geom.create_shape(settings, elem)
        if shape is None:
            return None
        
        points = np.array(shape.geometry.verts).reshape(-1, 3)
        min_point = points.min(axis=0)
        max_point = points.max(axis=0)
        center_point = ((min_point[0] + max_point[0]) / 2,
                        (min_point[1] + max_point[1]) / 2,
                        (min_point[2] + max_point[2]) / 2)
        
        bbox = {
            'min_point': min_point,
            'max_point': max_point,
            'center_point': center_point,
            'x_length': max_point[0] - min_point[0],
            'y_length': max_point[1] - min_point[1],
            'z_length': max_point[2] - min_point[2]
        }


        # print(f"Min point: {min_point},\nMax point: {max_point},\nCenter point: {center_point} ")
        # print(f"Lengths: x={bbox['x_length']:.4f}, y={bbox['y_length']:.4f}, z={bbox['z_length']:.4f}")
        
        return bbox
    except Exception as e:
        if (verbose):
            print(f"Error: {e}")
        return None

def get_related_elements_from_storey(elem:ifcopenshell.entity_instance, verbose:bool=False) -> list[str] | None:
    if(elem.is_a() != 'IFCBUILDINGSTOREY'):
        if(verbose):
            print(f"Error: Element is not a storey. Element is of type: {elem.is_a()}")
        return None
    
    related_elems = []
    for contains_elem in elem.ContainsElements:
        for related_elem in contains_elem.RelatedElements:
            related_elems.append(related_elem.id()) # could append the complete interval elem here
    return related_elems

def add_pset_attributes(psets) -> set:
    pset_attributes = set()
    for pset_name, pset_data in psets.items():
        for property_name in pset_data.keys():
            pset_attributes.add(f'{pset_name}.{property_name}')
    return pset_attributes

def get_objects_data_by_class(file, class_type):
    objects_data = []
    objects = file.by_type(class_type)

    for obj in objects:
        psets = element.get_psets(obj, psets_only=True)
        pset_attributes = add_pset_attributes(psets)
        qtos = element.get_psets(obj, qtos_only=True)
        qtos_attributes = add_pset_attributes(qtos)
        pset_attributes = pset_attributes.union(qtos_attributes)  # Join two sets

        bbox = get_bbox_test(obj)
        obj_info = obj.get_info()
        related_elems = get_related_elements_from_storey(obj) 

        objects_data.append({
            'id': obj.id(),
            'global_id': obj_info.get('GlobalId', None),
            'Class': obj.is_a(),
            'PredefinedType': element.get_predefined_type(obj),
            'name': obj_info.get('Name', None),
            'level': element.get_container(obj).Name if element.get_container(obj) else None,
            'ObjectType': element.get_type(obj).Name if element.get_type(obj) else None,
            'QuantitySets': qtos,
            'PropertySets': psets,
            'BBox': bbox,
            'obj':obj,
            'related_elements': related_elems
            #'Geometry': geometry
        })
        

    return objects_data, list(pset_attributes)

def compose_leapfrog_csv_data_from_elem_info(app_info: dict, intervals_data:list, collar_data:list, collar_filepath:str, intervals_filepath:str, verbose:bool=True) -> tuple[str,str] | None:
    if(app_info['ApplicationFullName'] != 'Leapfrog Works'):
        if(verbose):
            print(f"Error: Application is not Leapfrog Works. Application is: {app_info['ApplicationFullName']}")
        return None
    
    # 1) Get the intervals data into a csv readable format
    readable_intervals = []
    for interval in intervals_data:
        attributes = interval['PropertySets']['Attributes'] if (interval.get('PropertySets') and interval.get('PropertySets').get('Attributes')) else {}
        flat_interval = {**{
                'id': interval['id'],
                'global_id': interval['global_id'],
                'lithology_name': interval['name'], 
                'hole_id': interval['level'],
                'x': interval['BBox']['center_point'][0] if interval['BBox'] else None,
                'y': interval['BBox']['center_point'][1] if interval['BBox'] else None,
                'z': interval['BBox']['max_point'][2] if interval['BBox'] else None,
                'from_mNN': interval['BBox']['max_point'][2] if interval['BBox'] else None,
                'to_mNN': interval['BBox']['min_point'][2] if interval['BBox'] else None,
                'drilling_diameter': ((interval['BBox']['x_length'] + interval['BBox']['y_length']) / 2) if interval['BBox'] else None,
            }, **attributes
        }
        readable_intervals.append(flat_interval)

    # 2) Get the collar data into a csv readable format
    readable_collars = []
    for collar in collar_data:
        related_intervals = [interval for interval in readable_intervals if collar['name'] == interval['hole_id']]
        z = max([interval['z'] for interval in related_intervals]) if (len(related_intervals)>0) else None
        first_interval = [interval for interval in related_intervals if interval['z'] == z][0] if (len(related_intervals)>0) else None
        x = first_interval['x'] if first_interval else None
        y = first_interval['y'] if first_interval else None

        readable_collar = {
            "global_id": collar['global_id'],
            "hole_id": collar['name'],
            "x": x,
            "y": y,
            "z": z
        }
        readable_collars.append(readable_collar)
    
    # 3) Write the data to a csv file
    collar_filepath = write_list_of_dict_to_csv(readable_collars, collar_filepath)
    intervals_filepath = write_list_of_dict_to_csv(readable_intervals, intervals_filepath)
    return((collar_filepath, intervals_filepath))

if __name__ == "__main__":

    start_time = time.perf_counter()

    # 1) First Example - read the application info from an archicad generated ifc file
    ifc_boreholes = ifcopenshell.open("./data/leapfrog_examples/Boreholes_with_lithology.ifc")
    # haus = ifcopenshell.open("./data/AC20-FZK-Haus.ifc")
    # app_info = get_application(haus)

    # 2) Second Example - read the application info from a leapfrog works generated ifc file
    app_info = get_application(ifc_boreholes)
    print(f"Application: {app_info['ApplicationFullName']} {app_info['Version']}")

    # 3) Get Differnt elements from a borehole file from Leapfrog Works
    # data1, pset_attributes1 = get_objects_data_by_class(ifc_boreholes, 'ifcproject')
    # data2, pset_attributes2 = get_objects_data_by_class(ifc_boreholes, 'IFCCARTESIANPOINT')
    
    intervals_data, interval_pset_attributes = get_objects_data_by_class(ifc_boreholes, 'ifcbuildingelementproxy')
    collar_data, collar_pset_attributes = get_objects_data_by_class(ifc_boreholes, 'IFCBUILDINGSTOREY')

    # 4) Parse the extracted data into a csv file for further processing in leapfrog/other geotechnical software
    collar_csv, intervals_csv = compose_leapfrog_csv_data_from_elem_info(app_info, intervals_data, collar_data, './data/collar_data.csv', './data/intervals_data.csv')

    # pprint(interval_pset_attributes)
    # pprint(intervals_data)
    # IFCCIRCLEPROFILEDEF
    print(f"Execution time: {(time.perf_counter() - start_time):.4f} seconds")