import tkinter as tk
from tkinter import filedialog
import ifcopenshell
from ifcopenshell.api import run
import uuid
import ifcopenshell.template
import ifcopenshell.geom
import numpy as np
import ifcopenshell.util.placement

def open_ifc_file(file_path):
    return ifcopenshell.open(file_path)