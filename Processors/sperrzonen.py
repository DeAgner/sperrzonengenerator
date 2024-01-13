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



### Sperzonen erstellen

O = 0., 0., 0.
X = 1., 0., 0.
Y = 0., 1., 0.
Z = 0., 0., 1.

# Erzeugt ein IfcAxis2Placement3D aus Location, Axis und RefDirection, die als Python-Tupel angegeben sind
def create_ifcaxis2placement(ifcfile, point=O, dir1=Z, dir2=X):
    point = ifcfile.createIfcCartesianPoint(point)
    dir1 = ifcfile.createIfcDirection(dir1)
    dir2 = ifcfile.createIfcDirection(dir2)
    axis2placement = ifcfile.createIfcAxis2Placement3D(point, dir1, dir2)
    return axis2placement

# Erzeugt ein IfcLocalPlacement aus Location, Axis und RefDirection, angegeben als Python-Tupel, und relativer Platzierung
def create_ifclocalplacement(ifcfile, point=O, dir1=Z, dir2=X, relative_to=None):
    axis2placement = create_ifcaxis2placement(ifcfile,point,dir1,dir2)
    ifclocalplacement2 = ifcfile.createIfcLocalPlacement(relative_to,axis2placement)
    return ifclocalplacement2

# Erzeugt eine IfcPolyLine aus einer Liste von Punkten, die als Python-Tupel angegeben sind
def create_ifcpolyline(ifcfile, point_list):
    ifcpts = []
    for point in point_list:
        point = ifcfile.createIfcCartesianPoint(point)
        ifcpts.append(point)
    polyline = ifcfile.createIfcPolyLine(ifcpts)
    return polyline

# Erzeugt einen IfcExtrudedAreaSolid aus einer Liste von Punkten, die als Python-Tupel angegeben sind
def create_ifcextrudedareasolid(ifcfile, point_list, ifcaxis2placement, extrude_dir, extrusion):
    polyline = create_ifcpolyline(ifcfile, point_list)
    ifcclosedprofile = ifcfile.createIfcArbitraryClosedProfileDef("AREA", None, polyline)
    ifcdir = ifcfile.createIfcDirection(extrude_dir)
    ifcextrudedareasolid = ifcfile.createIfcExtrudedAreaSolid(ifcclosedprofile, ifcaxis2placement, ifcdir, extrusion)
    return ifcextrudedareasolid

