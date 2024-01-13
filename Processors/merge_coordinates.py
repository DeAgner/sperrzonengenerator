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

# Funktion, um Koordinaten innerhalb eines bestimmten Radius zu verschmelzen
def merge_coordinates_within_radius(coord_list, radius):
    merged_coords = []

    while coord_list:
        current_coord = coord_list.pop(0)
        close_coords = [current_coord]

        i = 0
        while i < len(coord_list):
            dist = np.linalg.norm(np.array(current_coord) - np.array(coord_list[i]))
            if dist <= radius:
                close_coords.append(coord_list.pop(i))
            else:
                i += 1

        # Mittelpunkt der nahen Koordinaten berechnen und hinzufügen
        if close_coords:
            merged_coords.append(np.mean(close_coords, axis=0))

    return merged_coords

