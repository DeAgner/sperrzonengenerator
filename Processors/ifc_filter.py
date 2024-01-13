import tkinter as tk
from tkinter import filedialog
import ifcopenshell
import ifcopenshell.util.element
from ifcopenshell.api import run
import uuid
import ifcopenshell.template
import ifcopenshell.geom
import numpy as np
import ifcopenshell.util.placement

# Funktion, um die GUIDs von IFC-Objekten zu erhalten, die ein bestimmtes Material verwenden
def get_ifc_object_guids_with_material(ifc_model, object_types, desired_materials):
    object_guid_list = []

    for object_type in object_types:
        objects = ifc_model.by_type(object_type)
        for obj in objects:
            materials = ifcopenshell.util.element.get_materials(obj)
            for material in materials:
                if any(desired in material.Name for desired in desired_materials):
                    object_guid_list.append(obj.GlobalId)

    return object_guid_list

# Funktion, um die transformierten Eckpunkte der Wände zu erhalten
def get_transformed_wall_vertices(ifc_file, guids):
    settings = ifcopenshell.geom.settings()
    mod_walls = []

    for guid in guids:
        wall = ifc_file.by_guid(guid)
        if wall:
            shape = ifcopenshell.geom.create_shape(settings, wall)
            verts = shape.geometry.verts
            matrix = ifcopenshell.util.placement.get_local_placement(wall.ObjectPlacement)
            transformed_verts = [np.dot(matrix, np.array(list(verts[i:i+3]) + [1]))[:3] for i in range(0, len(verts), 3)]
            mod_walls.append(transformed_verts)

    return mod_walls

# Funktion, um die transformierten Eckpunkte der Wände zu einer flachen Liste zu konvertieren
def flatten_wall_vertices(mod_walls):
    flat_array = np.concatenate(mod_walls)
    flat_list = flat_array.tolist()
    return flat_list
